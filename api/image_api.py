import asyncio
import time
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from api.packages.pb.packages_inspection import Image
from api.utils.connection_manager import ConnectionManager
from api.utils.camera import Camera
from threading import Thread

class ImageAPI(FastAPI):
    def __init__(self, title: str = "CustomAPI") -> None:
        super().__init__(title=title)
        self.manager = ConnectionManager() 
        self.camera = Camera()
        self.image_proto = Image()

        self.add_api_route('/capture-and-send', self.capture_and_send, methods=["GET"])
        self.add_api_websocket_route("/ws/camera/", self.websocket_endpoint)
    
    async def capture_and_send(self):
        url = "http://127.0.0.1:10101/classify-frame"
    
        response = requests.post(url, data=bytes(self.image_proto))
        
        if response.status_code == 200:
            return HTMLResponse(content=response.content, status_code=200)
        else:
            return HTMLResponse(status_code=500)
    
    async def send_images(self, websocket: WebSocket):
        try:
            while True:
                ret, frame = self.camera.get_frame()
                if not ret:
                    break
                self.image_proto.frame = self.camera.encode_image(frame)

                await websocket.send_text(bytes(self.image_proto))
                await asyncio.sleep(0.02)  # Use asyncio.sleep em vez de time.sleep
        except WebSocketDisconnect:
            print("WebSocket disconnected during image sending.")

    async def websocket_endpoint(self, *, websocket: WebSocket):
        await self.manager.connect(websocket)
        self.camera.set_camera('assets/1204.mp4')
        task = asyncio.create_task(self.send_images(websocket))
        try:
            await task  # Aguarda a conclusão da tarefa
        except WebSocketDisconnect:
            self.manager.disconnect(websocket)
        finally:
            task.cancel()  # Cancela a tarefa se algo der errado
            await task  # Certifica-se de que a tarefa é finalizada            

        
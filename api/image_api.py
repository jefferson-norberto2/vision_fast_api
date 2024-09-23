from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from pathlib import Path
from api.utils.connection_manager import ConnectionManager
from api.utils.camera import Camera

class ImageAPI(FastAPI):
    def __init__(self, title: str = "CustomAPI") -> None:
        super().__init__(title=title)
        self.manager = ConnectionManager() 
        self.cam = Camera()

        self.add_api_route('/', self.home, methods=["GET"])
        self.add_api_websocket_route("/ws/camera", self.websocket_endpoint)
        self.add_api_websocket_route("/sensors", self.show_sensors)
        

    async def home(self):
        html_file_path = Path("pages/home.html")
        html_content = html_file_path.read_text(encoding="utf-8")
        return HTMLResponse(html_content)
    
    async def show_sensors(self, *,
        websocket: WebSocket):
        await self.manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                print(f"Received data: {data}")  # Exibe os dados recebidos no console
        except WebSocketDisconnect:
            self.manager.disconnect(websocket)

    async def websocket_endpoint(
        self,
        *,
        websocket: WebSocket,
    ):
        await self.manager.connect(websocket)
        self.cam.set_camera(0)

        try:
            while True:
                ret, frame = self.cam.get_frame()
                if not ret:
                    break
                frame_data = self.cam.encode_image(frame)
                await websocket.send_text(frame_data)

        except WebSocketDisconnect:
            self.manager.disconnect(websocket)
        finally:
            self.cam.release_cam()
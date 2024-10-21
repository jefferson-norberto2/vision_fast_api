import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from api.packages.pb.packages_dispensation import Image
from api.utils.connection_manager import ConnectionManager
from api.utils.camera import Camera

class ImageAPI(FastAPI):
    def __init__(self, title: str = "CustomAPI") -> None:
        super().__init__(title=title)
        self.manager = ConnectionManager() 
        self.camera = Camera()
        self.image_proto = Image()

        self.add_api_route('/classify-frame', self.classify_frame, methods=["GET"])
        self.add_api_websocket_route("/ws/camera", self.websocket_endpoint)
    
    async def classify_frame(self):
        url = "http://127.0.0.1:101101/classify-image"
    
        response = requests.put(url, data=bytes(self.image_proto))
        
        if response.status_code == 200:
            return response
        else:
            return HTMLResponse(status_code=500)

    async def websocket_endpoint(
        self,
        *,
        websocket: WebSocket,
    ):
        await self.manager.connect(websocket)
        self.camera.set_camera(0)

        try:
            while True:
                ret, frame = self.camera.get_frame()
                if not ret:
                    break
                self.image_proto.frame = self.camera.encode_image(frame)

                await websocket.send_text(bytes(self.image_proto))

        except WebSocketDisconnect:
            self.manager.disconnect(websocket)
        finally:
            self.camera.release_cam()
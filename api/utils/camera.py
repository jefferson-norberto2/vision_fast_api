from cv2 import VideoCapture, imencode
from base64 import b64encode

class Camera:
    def __init__(self) -> None:
        self.cap = None
    
    def set_camera(self, cod: int):
        self.cap = VideoCapture(cod)
    
    def get_frame(self):
        return self.cap.read()            
    
    def encode_image(self, frame) -> str:
         _, buffer = imencode('.jpg', frame)
         frame_data = b64encode(buffer).decode('utf-8')
         return frame_data
    
    def release_cam(self):
        self.cap.release()
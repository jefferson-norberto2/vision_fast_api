from cv2 import VideoCapture, imencode, imdecode, IMREAD_COLOR
from base64 import b64encode, b64decode
import numpy as np

class Camera:
    def __init__(self) -> None:
        self.cap = None
    
    def set_camera(self, cod: int | str):
        self.cap = VideoCapture(cod)
    
    def get_frame(self):
        return self.cap.read()            
    
    def encode_image(self, frame) -> str:
         _, buffer = imencode('.jpg', frame)
         frame_data = b64encode(buffer).decode('utf-8')
         return frame_data
    
    def decode_image(self, encoded_frame: str):
        buffer = b64decode(encoded_frame)
        frame = np.frombuffer(buffer, dtype=np.uint8)
        image = imdecode(frame, IMREAD_COLOR)
        return image
    
    def release_cam(self):
        self.cap.release()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from api.packages.pb.packages_cme import Instrumental, Kit, KitList, InstrumentalList, Bbox, Classification, Image, Workbench, WorkbenchList
from api.utils.camera import Camera
from api.utils.onnx_opencv import detect
import yaml

class ServerAPI(FastAPI):
    def __init__(self, title: str = "CustomAPI") -> None:
        super().__init__(title=title)

        self.camera = Camera()

        self.add_api_route('/classify-frame', self.classify_frame, methods=["POST"])
        self.add_api_route('/inspection/workbench-list', self.workbench_list, methods=["GET"])
        self.add_api_route('/inspection/kit-list/{workbench_id}', self.kit_list, methods=["GET"])
        self.add_api_route('/inspection/instrument-list/{kit_id}', self.tool_list, methods=["GET"])

    async def workbench_list(self):
        table_list = WorkbenchList(workbenches=[])
        
        for i in range(5):
            table_list.workbenches.append(Workbench(id=i+1, name=f'Mesa {i+1}'))

        return HTMLResponse(content=bytes(table_list), status_code=200)


    async def kit_list(self, workbench_id):
        kit_list = KitList()
        workbench_id = int(workbench_id)
        if workbench_id == 1:
            kit_list.kits.append(Kit(id=1, name='Geral 01'))
            kit_list.kits.append(Kit(id=2, name='Geral 02'))
            kit_list.kits.append(Kit(id=3, name='Emergencia 01'))
        elif workbench_id == 2:
            kit_list.kits.append(Kit(id=11, name='Central 01'))
            kit_list.kits.append(Kit(id=21, name='Toracica 02'))
        elif workbench_id == 5:
            kit_list.kits.append(Kit(id=12, name='Laparoscopia 01'))
            kit_list.kits.append(Kit(id=42, name='Laparoscopia 02'))
            kit_list.kits.append(Kit(id=22, name='Trocater 01'))
            kit_list.kits.append(Kit(id=32, name='Gás e ótica 02'))

        return HTMLResponse(content=bytes(kit_list), status_code=200)
        

    async def tool_list(self, kit_id):
        instrumental_list = InstrumentalList(available_instrumental=[], unavailable_instrumental=[])
        kit_id = int(kit_id)

        if kit_id == 12:
            instrumental_list.unavailable_instrumental.append(Instrumental(id=0, name='Meryland'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=1, name='Aspirador 5mm'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=2, name='Hook em L'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=3, name='Debakey'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=4, name='Grasper'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=5, name='Clamp'))
        
        return HTMLResponse(content=bytes(instrumental_list), status_code=200)
    
    async def classify_frame(self, request: Request):
        data = await request.body()
        image_proto = Image().parse(data)
        image = self.camera.decode_image(image_proto.frame)

        with open('./assets/tools.yaml', 'r') as file:
            dict_yaml = yaml.safe_load(file)
        classes = dict_yaml["names"]

        results = detect('./assets/best.onnx', image, classes, 0.5)
        

        if len(results) > 0:
            result = results[0]
            inst = Instrumental(id=result['class_id'], name=result['class_name'])
            bbox = Bbox( x_min=result['bbox_n'][0], y_min=result['bbox_n'][1], width=result['bbox_n'][2], heigh=result['bbox_n'][3])
            classify = Classification(instrumental=inst, bbox=bbox, degree_confidence=result['confidence'])

            return HTMLResponse(content=bytes(classify), status_code=200)
        else:
            return HTMLResponse(status_code=500)
            
        
        # if response.status_code == 200:
        #     return response
        # else:
        #     return HTMLResponse(status_code=500)
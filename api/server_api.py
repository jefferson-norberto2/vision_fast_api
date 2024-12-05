
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from api.packages.pb.packages_common import Instrumental, Kit, KitList, InstrumentalList
from api.packages.pb.packages_inspection import Bbox, Classification, Image, Table, TableList
from api.utils.camera import Camera

class ServerAPI(FastAPI):
    def __init__(self, title: str = "CustomAPI") -> None:
        super().__init__(title=title)

        self.camera = Camera()

        self.add_api_route('/classify-frame', self.classify_frame, methods=["POST"])
        self.add_api_route('/inspection/workbench-list', self.workbench_list, methods=["GET"])
        self.add_api_route('/inspection/kit-list/{workbench_id}', self.kit_list, methods=["GET"])
        self.add_api_route('/inspection/tool-list/{kit_id}', self.tool_list, methods=["GET"])

    async def workbench_list(self):
        table_list = TableList(tables=[])
        
        for i in range(5):
            table_list.tables.append(Table(id=i+1, name=f'Mesa {i+1}'))

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
            instrumental_list.unavailable_instrumental.append(Instrumental(id=1, name='Hook em L'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=2, name='Debakey'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=3, name='Grasper'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=4, name='Porta agulha'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=5, name='Clamp'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=6, name='Aspirador 5mm'))
            instrumental_list.unavailable_instrumental.append(Instrumental(id=7, name='Meryland'))
        
        return HTMLResponse(content=bytes(instrumental_list), status_code=200)
    
    async def classify_frame(self, request: Request):
        data = await request.body()
        image_proto = Image().parse(data)

        image = self.camera.decode_image(image_proto.frame)
        print(image.shape)

        
        
        inst = Instrumental(id=1, name='Hook em L')
        bbox = Bbox(heigh=0.1, width=0.1, x_min=0.1, y_min=0.1)
        classify = Classification(instrumental=inst, bbox=bbox, degree_confidence=0.9)

        return HTMLResponse(content=bytes(classify), status_code=200)
        
        # if response.status_code == 200:
        #     return response
        # else:
        #     return HTMLResponse(status_code=500)
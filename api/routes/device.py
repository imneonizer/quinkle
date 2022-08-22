from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/list")
async def list_devices(request: Request):
    return request.app.devman.list()


@router.post("/register")
async def register_device(request: Request):
    return request.app.devman.register(await request.json())


@router.get("/{mac}/heartbeat")
async def heatbeat_device(mac: str, request: Request):
    return request.app.devman.heartbeat(mac)


@router.get("/{mac}/get")
async def get_device(mac: str, request: Request):
    return request.app.devman.get(mac)


@router.get("/{mac}/delete")
async def delete_device(mac: str, request: Request):
    return request.app.devman.delete(mac)


@router.get("/{mac}/request/{route}")
async def send_request_to_device(mac: str, route: str, request: Request):
    return request.app.devman.request(mac, {"route": route}, method="GET")


@router.post("/{mac}/request/{route}")
async def send_request_to_device(mac: str, route: str, data: dict, request: Request):
    return request.app.devman.request(mac, {"route": route, "data": data}, method="POST")

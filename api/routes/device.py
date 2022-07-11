from fastapi import APIRouter, Request

router = APIRouter()

@router.post('/register')
async def register_device(request : Request):
    return request.app.devman.register(await request.json())

@router.get('/heartbeat')
async def heatbeat_device(request: Request):
    return request.app.devman.heartbeat(request.query_params.get('mac'))

@router.get('/get')
async def get_device(request: Request):
    return request.app.devman.get(request.query_params.get('mac'))

@router.get('/list')
async def list_devices(request: Request):
    return request.app.devman.list()

@router.get('/delete')
async def delete_device(request: Request):
    return request.app.devman.delete(request.query_params.get('mac'))

@router.post('/request')
async def send_request_to_device(request: Request):
    return request.app.devman.request(request.query_params.get('mac'), await request.json())
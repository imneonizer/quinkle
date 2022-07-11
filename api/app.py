from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import config
from routes.device import router as device_router
from utils.device_manager import DeviceManager

app = FastAPI(default_response_class=JSONResponse)
app.devman = DeviceManager(
    redis_host=config.REDIS_HOST,
    redis_port=config.REDIS_PORT,
    redis_password=config.REDIS_PASSWORD,
    mqtt_host=config.MQTT_HOST,
    mqtt_port=config.MQTT_PORT
)

app.add_middleware(CORSMiddleware)
app.add_middleware(SessionMiddleware, secret_key=config.API_SECRET_KEY)
app.include_router(device_router, prefix="/device", tags=["device"])

# @app.on_event('startup')
# def mqtt_callbacks():
#     app.devman.start_mqtt_callback_threads()

@app.get('/')
async def root():
    return {"message": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        workers=4
    )

import asyncio
from fastapi.responses import HTMLResponse
from fastapi import WebSocket
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
    mqtt_port=config.MQTT_PORT,
)

app.add_middleware(CORSMiddleware)
app.add_middleware(SessionMiddleware, secret_key=config.API_SECRET_KEY)
app.include_router(device_router, prefix="/device", tags=["device"])


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:5000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send("/iot/mts/led_state")
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/html")
async def html_response():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    topic = await websocket.receive_text()
    sub_topic = "/iot/+/mts/+/events"

    while True:
        import time

        data = str(time.time())
        await websocket.send_text(f"topic: {topic}, data: {data}")
        await asyncio.sleep(2)


@app.get("/")
async def root():
    return {"message": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True, workers=4)

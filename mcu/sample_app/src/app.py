from lib.nodemcu import NodeMcu
from router import HandleMessages
from schema import schema
import time

app = NodeMcu(
    wifi_ssid="pluto",
    wifi_password="@universe101",
    mqtt_host="192.168.0.90",
    mqtt_port=2800,
    schema=schema
)


def main():
    # event loop callback
    msg = str(time.time())
    app.publish_event("time", msg)
    app.sleep(1)


HandleMessages(app)
app.run(main)

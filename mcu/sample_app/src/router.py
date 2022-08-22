from lib.nodemcu import Request
from machine import Pin

led = Pin(2, Pin.OUT)


class HandleMessages(Request):
    def __init__(self, app):
        self.app = app
        self.app.set_mqtt_callback(self)

    def led_state(self, msg, method):
        if method == "GET":
            return {"led_state": led.value()}

        elif method == "POST":
            value = msg.get("value", -1)
            if value == 0:
                led.on()
            elif value == 1:
                led.off()
            else:
                led.value(not led.value())

            self.app.publish_event("led_state", led.value())
            return {"led_state": led.value()}

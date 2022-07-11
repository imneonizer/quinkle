from lib.nodemcu import Request
from machine import Pin

led = Pin(2, Pin.OUT)

class HandleMessages(Request):
    def __init__(self, app):
        self.app = app
        self.app.set_mqtt_callback(self)
        self.print_messages = False
    
    def led_state(self, val):
        if val == 0:
            led.on()
        elif val == 1:
            led.off()
        else:
            led.value(not led.value())
        
        return {"led_state": led.value()}
import gc
import time
import machine
import network
import ubinascii
from lib.umqtt import MQTTClient
from lib.common.wifi import connect_wifi
import ujson as json


MAC_ADDR = ubinascii.hexlify(network.WLAN().config("mac"), ":").decode().lower()


class Topics:
    subscribe = b"/iot/%s/+/stm" % MAC_ADDR
    publish = b"/iot/%s/mts" % MAC_ADDR
    register = b"%s/register" % publish
    heartbeat = b"%s/heartbeat" % publish
    response = b"%s/msg_id/response" % publish
    events = b"%s/event_name/events" % publish


class Utils:
    def __init__(self):
        self.heartbeat_st = time.time()
        self.garbage_st = time.time()

    def connect(self):
        while True:
            try:
                connect_wifi(self.wifi_ssid, self.wifi_password, check=True)
                print("Connecting to MQTT broker....")
                self.mqtt.connect()
                self.mqtt.subscribe(self.topics.subscribe)
                print("Subscribed to %s" % self.topics.subscribe)
                break
            except Exception as e:
                print(e)
                time.sleep(1)

    def register(self, schema):
        while True:
            try:
                schema.update({"mac": MAC_ADDR})
                self.mqtt.publish(self.topics.register, json.dumps(schema))
                print("Registered Device = %s" % MAC_ADDR)
                break
            except Exception as e:
                print(e)
                time.sleep(1)

    def heartbeat(self):
        if (time.time() - self.heartbeat_st) > 1:
            self.heartbeat_st = time.time()
            self.mqtt.publish(self.topics.heartbeat, MAC_ADDR.encode())

    def garbage_collector(self):
        if (time.time() - self.garbage_st) > 1:
            self.garbage_st = time.time()
            gc.collect()

    def sleep(self, t=0, delay=0.03):
        st = time.time()
        while (time.time() - st) < t:
            try:
                self.callbacks()
            except Exception as e:
                print(e)
            time.sleep(delay if t > delay else t)


class NodeMcu(Utils):
    def __init__(self, wifi_ssid, wifi_password, mqtt_host, mqtt_port, schema):
        Utils.__init__(self)
        self.topics = Topics()
        self.schema = schema
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.mqtt = MQTTClient(MAC_ADDR, server=mqtt_host, port=mqtt_port)

    def set_mqtt_callback(self, callback):
        def callback_wrapper(client, topic, msg):
            response = callback(client, topic, msg)
            if response:
                msg_id = topic.decode().split("/")[3]
                resp_topic = b"%s/%s/response" % (self.topics.publish, msg_id)
                client.publish(resp_topic, json.dumps(response))

        self.mqtt.set_callback(callback_wrapper)

    def callbacks(self):
        try:
            self.mqtt.check_msg()
            self.heartbeat()
            self.garbage_collector()
        except Exception as e:
            print(e)
            time.sleep(5)
            machine.reset()

    def publish_event(self, event_name, data):
        event_topic = b"%s/%s/events" % (self.topics.publish, event_name)
        if not isinstance(data, str):
            data = str(data)
        self.mqtt.publish(event_topic, data)

    def run(self, target=None, *args, **kwargs):
        self.connect()
        self.register(self.schema)

        while True:
            self.callbacks()
            target and target(*args, **kwargs)


class Request:
    OK = {"msg": "ok"}

    def get_route_handler(self, route):
        if hasattr(self, route):
            return getattr(self, route)

    def __call__(self, client, topic, msg):
        try:
            msg = json.loads(msg)
        except Exception as e:
            print(e)
            return {"msg": "Unable to parse message, error: %s" % e, "status_code": 500}

        # print(msg)

        method = msg.pop("method", "")
        route = msg.pop("route", "unknown")
        route_handler = self.get_route_handler(route)

        if not route_handler:
            return {"msg": "route %s doesn't exists" % route, "status_code": 404}

        return route_handler(msg.pop("data", {}), method=method)

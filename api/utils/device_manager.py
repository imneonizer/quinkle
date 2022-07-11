import redis
import ujson
import time
from fastapi import HTTPException
import paho.mqtt.client as mqtt
import ujson as json
import uuid


class DeviceManager:
    OK = {"msg": "ok"}

    def __init__(self, redis_host, redis_port, redis_password, mqtt_host, mqtt_port):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password
        )

        self.mqtt = mqtt.Client()
        self.connect_mqtt()

    def connect_mqtt(self):
        while True:
            try:
                print("trying to connect mqtt")
                self.mqtt.connect(self.mqtt_host, self.mqtt_port)
                self.mqtt.loop_start()
                break
            except Exception as e:
                print(e)
                time.sleep(1)
                

    def register(self, meta):
        mac = meta.get('mac', '')
        self.redis.set(f"device/{mac}", ujson.dumps(meta))
        self.redis.set(f"updated_at/{mac}", time.time())
        return self.OK

    def heartbeat(self, mac):
        self.redis.set(f"updated_at/{mac}", time.time())
        return self.OK

    def get(self, mac):
        device = self.redis.get(f"device/{mac}")
        if device is not None:
            device = ujson.loads(device)
            updated_at = int(float(self.redis.get(f"updated_at/{mac}") or 0))
            device.update({"alive": True, "last_seen": updated_at})
            if time.time() - updated_at > device.get("heartbeat_interval", 10):
                device.update({"alive": False})
            return device
        raise HTTPException(status_code=400, detail="no device found")

    def list(self):
        devices = []
        for key in self.redis.scan_iter("device/*"):
            mac = key.decode().lstrip("device/")
            device = self.get(mac)
            devices.append(device)
        return devices

    def delete(self, mac):
        self.redis.delete(f"device/{mac}")
        self.redis.delete(f"updated_at/{mac}")
        return self.OK

    def request(self, mac, meta):        
        msg_id = str(uuid.uuid4())[:8]
        topic = f"/iot/{mac}/{msg_id}/stm"
        try:
            self.mqtt.publish(topic, json.dumps(meta))
        except: pass

        st = time.time()
        response_timeout = 2
        while True:
            msg_key = f"/response/{msg_id}"
            response = self.redis.get(msg_key)
            if response:
                response = json.loads(response)
                self.redis.delete(msg_key)
                return response
            elif (time.time() - st > response_timeout):
                return {"msg": "timeout"}
        return {"msg": "device unreachable"}

import os
import time
import redis
import threading
import ujson as json
import paho.mqtt.client as mqtt


class MqttCallbacks:
    def __init__(self, redis_host, redis_port, redis_password, mqtt_host, mqtt_port):
        self.mqtt_host, self.mqtt_port = (mqtt_host, mqtt_port)

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
                self.mqtt.connect(self.mqtt_host, self.mqtt_port)
                self.mqtt.loop_start()
                break
            except Exception as e:
                print(e)
                time.sleep(1)

    def subscribe(self, topic, callback):
        while True:
            try:
                client = mqtt.Client()
                client.on_connect = lambda client, userdata, flags, rc: client.subscribe(
                    topic)
                client.on_message = callback
                client.connect(self.mqtt_host, self.mqtt_port)
                client.loop_forever()
            except Exception as e:
                print(e)
                time.sleep(1)

    def create_thread(self, topic, callback):
        return threading.Thread(
            target=self.subscribe,
            args=(topic, callback,)
        )

    def register(self, topic="/iot/+/mts/register"):
        """
        listen for device registeration messages from mqtt
        and write to redis.
        """
        def on_message(client, userdata, msg):
            # decode received message
            topic = str(msg.topic)
            message = str(msg.payload.decode("utf-8"))
            message = json.loads(message)

            # update device meta to redis
            mac = message.get('mac', '')
            self.redis.set(f"device/{mac}", json.dumps(message))
            self.redis.set(f"updated_at/{mac}", time.time())

        return self.create_thread(topic, on_message).start()

    def heartbeat(self, topic="/iot/+/mts/heartbeat"):
        def on_message(client, userdata, msg):
            # decode received message
            mac = str(msg.payload.decode("utf-8"))
            
            # updated heartbeat time to redis
            self.redis.set(f"updated_at/{mac}", time.time())

        return self.create_thread(topic, on_message).start()

    def response(self, msg_expire=5, topic="/iot/+/mts/+/response"):
        def on_message(client, userdata, msg):
            msg_id = msg.topic.split("/")[4]
            msg_id = f"/response/{msg_id}"
            msg = json.loads(str(msg.payload.decode("utf-8")))
            self.redis.set(msg_id, json.dumps(msg))
            self.redis.expire(msg_id, msg_expire)
        return self.create_thread(topic, on_message).start()

    def run(self, msg_expire=5):
        self.register()
        self.heartbeat()
        self.response(msg_expire)


if __name__ == "__main__":
    print("Started mqtt callbacks...")
    MqttCallbacks(
        redis_host=os.environ.get('REDIS_HOST', 'redis'),
        redis_port=int(os.environ.get('REDIS_PORT', 6379)),
        redis_password=os.environ.get('REDIS_PASSWORD', 'quinkle'),
        mqtt_host=os.environ.get('MQTT_HOST', 'mosquitto'),
        mqtt_port=int(os.environ.get('REDIS_PORT', 1883))
    ).run(msg_expire=5)
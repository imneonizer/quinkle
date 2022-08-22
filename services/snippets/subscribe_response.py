import paho.mqtt.client as mqtt
import time

sub_topic = "/iot/+/mts/+/response"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print(f"Subscribed to {sub_topic}")
    client.subscribe(sub_topic)

def on_message(client, userdata, msg):
    msg_id = msg.topic.split("/")[4]
    message = str(msg.payload.decode("utf-8"))
    # print(int(time.time()), topic, message)
    print(msg_id)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.0.90", 2800)
client.loop_forever()
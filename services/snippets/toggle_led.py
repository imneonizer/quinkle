import requests

# res = requests.get("http://localhost:5000/device/48:3f:da:79:7e:7d/request/led_state")
# print(res.text)

res = requests.post("http://localhost:5000/device/48:3f:da:79:7e:7d/request/led_state", json={"value": -1})
print(res.text)
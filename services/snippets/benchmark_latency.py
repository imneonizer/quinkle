import requests
import time
import threading


def target(i):
    while True:
        st = time.time()
        res = requests.post(
            "http://localhost:5000/device/48:3f:da:79:7e:7d/request/set_led_state",
            json={"value": -1},
        )

        print(res.text)
        print(f"elapsed => {((time.time() - st) * 1000):.0f} ms")
        # time.sleep(0.03)


threads = []
for i in range(1):
    t = threading.Thread(target=target, args=(i,))
    threads.append(t)
    t.start()

for i in threads:
    t.join()

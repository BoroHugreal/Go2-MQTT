import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client()
client.connect("localhost", 1883)
client.loop_start()
while True:
    pos = {"x": 2.37556, "y": 48.77713}
    client.publish("robot/position", json.dumps(pos))
    print(f"Publié : {pos}")
    time.sleep(1)
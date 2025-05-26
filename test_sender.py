import paho.mqtt.client as mqtt
import json

client = mqtt.Client()
client.connect("localhost", 1883)
client.loop_start()
client.publish("robot/commands", json.dumps({"command": "BalanceStand"}))
client.loop_stop()
client.disconnect()

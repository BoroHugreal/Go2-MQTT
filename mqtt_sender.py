import paho.mqtt.client as mqtt
import json
from .config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

def send_command(command_name):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()
    payload = json.dumps({"command": command_name})
    client.publish(MQTT_TOPIC, payload=payload)
    client.loop_stop()
    client.disconnect()

# Fonction pour envoyer un chemin au robot
def send_path(path_coords):
    client = mqtt.Client()
    client.connect("localhost", 1883)
    client.loop_start()
    payload = json.dumps({"path": path_coords})
    client.publish("robot/path", payload=payload)
    client.loop_stop()
    client.disconnect()
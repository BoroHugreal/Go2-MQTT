# app/mqtt_position_listener.py
# -*- coding: utf-8 -*-
"""
# Écoute des positions du robot via MQTT
"""

import threading
import paho.mqtt.client as mqtt
import json
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_POSITION

# Definition de la dernière position du robot
last_position = {"x": 2.37556, "y": 48.77713, "yaw": 0, "speed": 0.0}

# Fonction de rappel pour la réception des messages MQTT
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Position MQTT reçue : {payload}")
        last_position["x"] = payload.get("x", 0)
        last_position["y"] = payload.get("y", 0)
        last_position["speed"] = payload.get("speed", 0.0)
        if "yaw" in payload:
            last_position["yaw"] = payload.get("yaw", 0)
    except Exception as e:
        print(f"Erreur de décodage position: {e}")

# Fonction pour démarrer l'écoute des positions MQTT
def start_position_listener(broker=MQTT_BROKER, port=MQTT_PORT, topic=MQTT_TOPIC_POSITION):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe(topic)
    client.loop_start()
    return client

# Fonction pour démarrer l'écoute des positions dans un thread
def run_position_listener(broker=MQTT_BROKER, port=MQTT_PORT, topic=MQTT_TOPIC_POSITION):
    thread = threading.Thread(target=start_position_listener, args=(broker, port, topic), daemon=True)
    thread.start()
# app/mqtt_ack_listener.py
# -*- coding: utf-8 -*-
"""
# Écoute des accusés de réception des commandes via MQTT
"""

import threading
import json
import paho.mqtt.client as mqtt
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_ACK

last_ack = {"command": None, "status": None}

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        last_ack["command"] = payload.get("command")
        last_ack["status"] = payload.get("status")
    except json.JSONDecodeError:
        pass

def start_ack_listener(broker=MQTT_BROKER, port=MQTT_PORT, topic=MQTT_TOPIC_ACK):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe(topic)
    client.loop_start()
    return client

def run_listener(broker=MQTT_BROKER, port=MQTT_PORT, topic=MQTT_TOPIC_ACK):
    thread = threading.Thread(target=start_ack_listener, args=(broker, port, topic), daemon=True)
    thread.start()
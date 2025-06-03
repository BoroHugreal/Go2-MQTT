# app/mqtt_state_listener.py
# -*- coding: utf-8 -*-
"""
# Écoute des états du robot via MQTT
"""

import threading
import paho.mqtt.client as mqtt
import json

# Variables globales protégées
last_state = {"mode": "inconnu", "battery": 0, "status": "inconnu"}
last_state_lock = threading.Lock()
mqtt_connected = False
mqtt_connected_lock = threading.Lock()

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    with mqtt_connected_lock:
        mqtt_connected = (rc == 0)
    print(f"MQTT connecté : {mqtt_connected}, code retour : {rc}")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    with mqtt_connected_lock:
        mqtt_connected = False
    print(f"MQTT déconnecté, code retour : {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"État MQTT reçu : {payload}")
        with last_state_lock:
            last_state["mode"] = payload.get("mode", "inconnu")
            last_state["battery"] = payload.get("battery", 0)
            last_state["status"] = payload.get("status", "inconnu")
    except Exception as e:
        print(f"Erreur de décodage état: {e}")

def get_state():
    with last_state_lock:
        return last_state.copy()

def get_mqtt_status():
    with mqtt_connected_lock:
        return mqtt_connected

def start_state_listener(broker, port, topic):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe(topic)
    client.loop_start()
    return client

def run_state_listener(broker, port, topic):
    thread = threading.Thread(target=start_state_listener, args=(broker, port, topic), daemon=True)
    thread.start()
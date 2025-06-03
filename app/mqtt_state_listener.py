# app/mqtt_state_listener.py
# -*- coding: utf-8 -*-
"""
# Écoute des états du robot via MQTT
"""

import threading
import paho.mqtt.client as mqtt
import json

# Variable globale pour stocker le dernier état reçu
last_state = {"mode": "inconnu", "battery": 0, "status": "inconnu"}

# Fonction de rappel pour la réception des messages MQTT
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"État MQTT reçu : {payload}")
        last_state["mode"] = payload.get("mode", "inconnu")
        last_state["battery"] = payload.get("battery", 0)
        last_state["status"] = payload.get("status", "inconnu")
    except Exception as e:
        print(f"Erreur de décodage état: {e}")

# Fonction pour démarrer l'écoute des états MQTT
def start_state_listener(broker, port, topic):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe(topic)
    client.loop_start()
    return client

# Fonction pour démarrer l'écoute des états dans un thread
def run_state_listener(broker, port, topic):
    thread = threading.Thread(target=start_state_listener, args=(broker, port, topic), daemon=True)
    thread.start()
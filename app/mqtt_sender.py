# app/mqtt_sender.py
# -*- coding: utf-8 -*-
"""
# Envoi de commandes et de chemins via MQTT avec gestion d'erreur
"""

import paho.mqtt.client as mqtt
import json
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_COMMAND, MQTT_TOPIC_PATH

# Fonction pour envoyer une commande au robot via MQTT
def send_command(command_name):
    client = mqtt.Client()
    try:
        client.username_pw_set("admin", "L!ss!2025")  # ← AJOUT
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()
        payload = json.dumps({"command": command_name})
        result = client.publish(MQTT_TOPIC_COMMAND, payload=payload)
        client.loop_stop()
        client.disconnect()
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Erreur publication commande MQTT, code: {result.rc}")
    except Exception as e:
        raise RuntimeError(f"Erreur envoi commande MQTT: {e}")

# Fonction pour envoyer un chemin au robot via MQTT
def send_path(path_coords):
    client = mqtt.Client()
    try:
        client.username_pw_set("admin", "L!ss!2025")  # ← AJOUT
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()
        payload = json.dumps({"path": path_coords})
        result = client.publish(MQTT_TOPIC_PATH, payload=payload)
        client.loop_stop()
        client.disconnect()
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Erreur publication chemin MQTT, code: {result.rc}")
    except Exception as e:
        raise RuntimeError(f"Erreur envoi chemin MQTT: {e}")
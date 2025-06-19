# app/mqtt_sender.py
# -*- coding: utf-8 -*-
""""
API Flask pour l'envoi de commandes et de chemins au robot Go2 via MQTT.
"""

from .mqtt_manager import mqtt_manager  # On importe l'instance globale créée dans mqtt_manager.py
from app.config import MQTT_TOPIC_COMMAND, MQTT_TOPIC_PATH
import json

def send_command(command):
    payload = json.dumps({"command": command})
    return mqtt_manager.publish(MQTT_TOPIC_COMMAND, payload)

def send_path(path_coords):
    payload = json.dumps({"waypoints": path_coords})
    return mqtt_manager.publish(MQTT_TOPIC_PATH, payload)

def check_mqtt_connection():
    return mqtt_manager.is_connected()
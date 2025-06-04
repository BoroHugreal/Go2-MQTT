# app/mqtt_video_listener.py
# -*- coding: utf-8 -*-
"""
Écoute du flux vidéo du robot via MQTT
"""

import threading
import paho.mqtt.client as mqtt
import base64
import logging
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_VIDEO

# Buffer pour stocker la dernière frame reçue
last_frame = None
last_frame_lock = threading.Lock()
video_connected = False
video_connected_lock = threading.Lock()

logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc):
    global video_connected
    with video_connected_lock:
        video_connected = (rc == 0)
    logger.info(f"MQTT Vidéo connecté : {video_connected}, code retour : {rc}")

def on_disconnect(client, userdata, rc):
    global video_connected
    with video_connected_lock:
        video_connected = False
    logger.info(f"MQTT Vidéo déconnecté, code retour : {rc}")

def on_message(client, userdata, msg):
    global last_frame
    try:
        # Le robot envoie les frames en base64
        frame_data = base64.b64decode(msg.payload)
        with last_frame_lock:
            last_frame = frame_data
        logger.debug("Frame vidéo MQTT reçue")
    except Exception as e:
        logger.error(f"Erreur de décodage frame vidéo: {e}")

def get_last_frame():
    with last_frame_lock:
        return last_frame

def get_video_status():
    with video_connected_lock:
        return video_connected

def start_video_listener(broker, port, topic):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    try:
        client.connect(broker, port)
        client.subscribe(topic)
        client.loop_start()
        logger.info(f"Listener vidéo MQTT démarré sur {topic}")
        return client
    except Exception as e:
        logger.error(f"Erreur connexion MQTT vidéo: {e}")
        return None

def run_video_listener(broker, port, topic):
    thread = threading.Thread(
        target=start_video_listener, 
        args=(broker, port, topic), 
        daemon=True
    )
    thread.start()

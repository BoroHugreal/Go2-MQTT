# tools/simulate_position.py
# -*- coding: utf-8 -*-
"""
Ce script simule la publication de la position d'un robot sur un broker MQTT.
Il envoie périodiquement des données de position sous forme de JSON.
Il utilise la bibliothèque Paho MQTT pour gérer les connexions et les messages.
Il est conçu pour être utilisé dans un environnement de développement ou de test,
afin de simuler le comportement d'un robot Go2.
"""

import paho.mqtt.client as mqtt
import json
import time
import logging

logging.basicConfig(level=logging.INFO)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connecté au broker MQTT")
    else:
        logging.error(f"Connexion échouée : code {rc}")

def on_disconnect(client, userdata, rc):
    logging.warning("Déconnecté du broker MQTT")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect("localhost", 1883)
        client.loop_start()

        while True:
            pos = {"x": 2.37556, "y": 48.77713}
            client.publish("robot/position", json.dumps(pos))
            logging.info(f"Publié : {pos}")
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Simulation stoppée par l'utilisateur.")
    except Exception:
        logging.exception("Erreur dans simulate_position")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()

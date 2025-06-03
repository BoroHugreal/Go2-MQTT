# tools/test_sender.py
# -*- coding: utf-8 -*-
"""
Ce script est un client MQTT qui se connecte à un broker local,
s'abonne à un topic spécifique et envoie une commande de test.
Il utilise la bibliothèque Paho MQTT pour gérer les connexions et les messages.
Il est conçu pour être utilisé dans un environnement de développement ou de test,
afin de vérifier la publication de messages MQTT.
"""

import paho.mqtt.client as mqtt
import json
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
        result = client.publish("robot/commands", json.dumps({"command": "BalanceStand"}))
        result.wait_for_publish()
        if result.is_published():
            logging.info("Commande publiée avec succès.")
        else:
            logging.warning("Échec de la publication.")
    except Exception:
        logging.exception("Erreur dans test_sender")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
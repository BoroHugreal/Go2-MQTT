# tools/receiver_debug.py
# -*- coding: utf-8 -*-
"""
Ce script est un client MQTT qui se connecte à un broker local,
s'abonne à un topic spécifique et affiche les messages reçus.
Il utilise la bibliothèque Paho MQTT pour gérer les connexions et les messages.
Il est conçu pour être utilisé dans un environnement de développement ou de test,
afin de déboguer la réception de messages MQTT.
"""

import paho.mqtt.client as mqtt
import logging

logging.basicConfig(level=logging.INFO)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connecté au broker MQTT")
        client.subscribe("robot/commands")
    else:
        logging.error(f"Échec de connexion : code {rc}")

def on_disconnect(client, userdata, rc):
    logging.warning("Déconnecté du broker MQTT")

def on_message(client, userdata, message):
    logging.info(f"Message reçu : {message.payload.decode()}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        client.connect("localhost", 1883)
        client.loop_forever()
    except Exception as e:
        logging.exception("Erreur lors de l'exécution MQTT")

if __name__ == "__main__":
    main()
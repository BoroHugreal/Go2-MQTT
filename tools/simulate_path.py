# tools/simulate_path.py
# -*- coding: utf-8 -*-
"""
Ce script simule le déplacement d'un robot le long d'un chemin prédéfini 
en publiant périodiquement sa position sur un broker MQTT.
Il utilise la bibliothèque Paho MQTT pour gérer les connexions et les messages.
Il est conçu pour être utilisé dans un environnement de développement ou de test, 
afin de simuler le comportement d'un robot Go2.
"""

import paho.mqtt.client as mqtt
import json
import time
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Liste des points (latitude, longitude)
path = [
    (48.777164396, 2.375696799),
    (48.777266135, 2.375488087),
    (48.777245920, 2.375302510),
    (48.777219946, 2.374943893),
    (48.777252453, 2.375237042),
    (48.777247827, 2.375732456),
    (48.777378526, 2.375937183),
    (48.777426862, 2.376234988),
    (48.777376616, 2.376366631),
    (48.777280918, 2.376314928),
    (48.777184431, 2.376204572),
    (48.777053307, 2.376061392),
    (48.777101311, 2.375851686),
]

BROKER = "localhost"
PORT = 1883
TOPIC = "robot/position"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connexion réussie au broker MQTT.")
    else:
        logging.error(f"Échec de connexion : code {rc}")
        sys.exit(1)

def on_disconnect(client, userdata, rc):
    logging.warning("Déconnexion du broker MQTT.")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()
        logging.info("Début de la simulation du déplacement du robot.")

        for lat, lon in path:
            pos = {"x": lon, "y": lat}
            res = client.publish(TOPIC, json.dumps(pos))
            res.wait_for_publish()
            if res.rc != mqtt.MQTT_ERR_SUCCESS:
                logging.error(f"Erreur lors de la publication : code {res.rc}")
            else:
                logging.info(f"Publié : {pos}")
            time.sleep(1)

        logging.info("Chemin terminé.")

    except KeyboardInterrupt:
        logging.info("Simulation interrompue par l'utilisateur.")
    except Exception:
        logging.exception("Erreur pendant la simulation.")
    finally:
        client.loop_stop()
        client.disconnect()
        logging.info("Client MQTT déconnecté.")

if __name__ == "__main__":
    main()
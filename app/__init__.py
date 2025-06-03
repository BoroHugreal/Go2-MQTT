# -*- coding: utf-8 -*-
"""
Initialisation de l'application Flask et des listeners MQTT
"""

import os
import logging
from flask import Flask
from .routes import bp
from .config import MQTT_BROKER, MQTT_PORT
from .mqtt_ack_listener import run_listener
from .mqtt_position_listener import run_position_listener
from .mqtt_state_listener import run_state_listener

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def create_app():
    app = Flask(__name__)
    
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "unsafe-default-key")
    if app.secret_key == "unsafe-default-key":
        logging.warning("FLASK_SECRET_KEY non défini, utilisez une variable d’environnement pour plus de sécurité.")
    
    app.register_blueprint(bp)

    try:
        logging.info("Démarrage des listeners MQTT.")
        run_listener(MQTT_BROKER, MQTT_PORT, "robot/ack")
        run_position_listener(MQTT_BROKER, MQTT_PORT, "robot/position")
        run_state_listener(MQTT_BROKER, MQTT_PORT, "robot/state")
    except Exception as e:
        logging.exception("Erreur lors de l'initialisation des listeners MQTT.")

    return app
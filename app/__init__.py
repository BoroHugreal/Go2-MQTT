from flask import Flask
from .routes import bp
from .config import MQTT_BROKER, MQTT_PORT
from .mqtt_ack_listener import run_listener
from .mqtt_position_listener import run_position_listener
from .mqtt_state_listener import run_state_listener

# app/__init__.py
# Initialisation de l'application Flask et des listeners MQTT
# -*- coding: utf-8 -*-

"""
Initialisation de l'application Flask et des listeners MQTT
"""

def create_app():
    app = Flask(__name__)
    app.secret_key = "change_this_secret_key"
    app.register_blueprint(bp)
    run_listener(MQTT_BROKER, MQTT_PORT, "robot/ack") # Ce listener est pour les accusés de réception
    run_position_listener(MQTT_BROKER, MQTT_PORT, "robot/position")  # Ce listener est pour la position du robot
    run_state_listener(MQTT_BROKER, MQTT_PORT, "robot/state")  # Ce listener est pour l'état du robot
    return app
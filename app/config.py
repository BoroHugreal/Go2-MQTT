# app/config.py
# -*- coding: utf-8 -*-
# Configuration des paramètres MQTT pour l'application

MQTT_BROKER = "91.108.112.88"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_ACK = "robot/ack"
MQTT_TOPIC_POSITION = "robot/position"
MQTT_TOPIC_PATH = "robot/path"
MQTT_TOPIC_STATE = "robot/state"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_JOYSTICK = "robot/joystick"
# app/mqtt_sender.py
from .mqtt_manager import mqtt_manager
from app.config import MQTT_TOPIC_COMMAND, MQTT_TOPIC_PATH
import json

SPORT_CMD = {
    "Damp": 1001, "BalanceStand": 1002, "StopMove": 1003, "StandUp": 1004,
    "StandDown": 1005, "RecoveryStand": 1006, "Euler": 1007, "Move": 1008,
    "Sit": 1009, "RiseSit": 1010, "SwitchGait": 1011, "Trigger": 1012,
    "BodyHeight": 1013, "FootRaiseHeight": 1014, "SpeedLevel": 1015,
    "Hello": 1016, "Stretch": 1017, "TrajectoryFollow": 1018,
    "ContinuousGait": 1019, "Content": 1020, "Wallow": 1021,
    "Dance1": 1022, "Dance2": 1023, "GetBodyHeight": 1024,
    "GetFootRaiseHeight": 1025, "GetSpeedLevel": 1026,
    "SwitchJoystick": 1027, "Pose": 1028, "Scrape": 1029,
    "FrontFlip": 1030, "FrontJump": 1031, "FrontPounce": 1032,
    "WiggleHips": 1033, "GetState": 1034, "EconomicGait": 1035,
    "FingerHeart": 1036,
}

def send_command(command_name):
    if command_name in SPORT_CMD:
        code = SPORT_CMD[command_name]
        payload = json.dumps({"command": code})
        return mqtt_manager.publish(MQTT_TOPIC_COMMAND, payload)
    else:
        print(f"Commande inconnue: {command_name}")
        return False

def send_path(path_coords):
    payload = json.dumps({"waypoints": path_coords})
    return mqtt_manager.publish(MQTT_TOPIC_PATH, payload)

def check_mqtt_connection():
    return mqtt_manager.is_connected()
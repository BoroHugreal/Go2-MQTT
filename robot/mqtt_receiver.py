# robot/mqtt_receiver.py
# -*- coding: utf-8 -*-
"""
Écoute des commandes du robot via MQTT
"""

import asyncio
import json
import logging
import signal
import sys
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

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

from app.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_COMMAND, MQTT_TOPIC_ACK

command_queue = asyncio.Queue()
loop = asyncio.get_event_loop()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("MQTT connected.")
        client.subscribe(MQTT_TOPIC_COMMAND)
    else:
        logging.error(f"MQTT connection failed: code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        command_name = payload.get("command")
        if command_name in SPORT_CMD:
            logging.info(f"Received command: {command_name}")
            asyncio.run_coroutine_threadsafe(command_queue.put(command_name), loop)
        else:
            logging.warning(f"Unknown command received: {command_name}")
    except json.JSONDecodeError:
        logging.error("Invalid JSON received.")
    except Exception as e:
        logging.exception(f"Exception in message handling: {e}")

def setup_mqtt():
    client = mqtt.Client()
    client.username_pw_set("admin", "L!ss!2025")
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {e}")
        sys.exit(1)
    return client

def setup_ack_client():
    client = mqtt.Client()
    client.username_pw_set("admin", "L!ss!2025") 
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
    except Exception as e:
        logging.error(f"Failed to connect ACK client: {e}")
        sys.exit(1)
    return client

ack_client = setup_ack_client()

def send_ack(command_name, status="received"):
    ack_payload = json.dumps({"command": command_name, "status": status})
    result = ack_client.publish(MQTT_TOPIC_ACK, ack_payload)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logging.info(f"ACK sent: {command_name} ({status})")
    else:
        logging.error(f"Failed to send ACK for: {command_name}")

async def handle_commands():
    logging.info("Command handler active.")
    while True:
        command_name = await command_queue.get()
        logging.info(f"Executing: {command_name} (ID: {SPORT_CMD[command_name]})")
        try:
            # Appel vers robot réel ici
            await asyncio.sleep(2)
            send_ack(command_name, "received")
        except Exception as e:
            logging.exception(f"Error executing command {command_name}: {e}")
            send_ack(command_name, "error")

def shutdown():
    logging.info("Shutting down...")
    ack_client.loop_stop()
    ack_client.disconnect()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: shutdown())
    signal.signal(signal.SIGTERM, lambda s, f: shutdown())
    setup_mqtt()
    try:
        loop.run_until_complete(handle_commands())
    except Exception as e:
        logging.exception(f"Fatal error: {e}")
    finally:
        shutdown()
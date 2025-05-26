import asyncio
import json
import paho.mqtt.client as mqtt

# Mapping nom → ID
SPORT_CMD = {
    "Damp": 1001,
    "BalanceStand": 1002,
    "StopMove": 1003,
    "StandUp": 1004,
    "StandDown": 1005,
    "RecoveryStand": 1006,
    "Euler": 1007,
    "Move": 1008,
    "Sit": 1009,
    "RiseSit": 1010,
    "SwitchGait": 1011,
    "Trigger": 1012,
    "BodyHeight": 1013,
    "FootRaiseHeight": 1014,
    "SpeedLevel": 1015,
    "Hello": 1016,
    "Stretch": 1017,
    "TrajectoryFollow": 1018,
    "ContinuousGait": 1019,
    "Content": 1020,
    "Wallow": 1021,
    "Dance1": 1022,
    "Dance2": 1023,
    "GetBodyHeight": 1024,
    "GetFootRaiseHeight": 1025,
    "GetSpeedLevel": 1026,
    "SwitchJoystick": 1027,
    "Pose": 1028,
    "Scrape": 1029,
    "FrontFlip": 1030,
    "FrontJump": 1031,
    "FrontPounce": 1032,
    "WiggleHips": 1033,
    "GetState": 1034,
    "EconomicGait": 1035,
    "FingerHeart": 1036,
}

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_ACK = "robot/ack"

command_queue = asyncio.Queue()
loop = asyncio.get_event_loop()

# Client MQTT pour recevoir les commandes
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        command_name = payload.get("command")
        if command_name in SPORT_CMD:
            print(f"Received command via MQTT: {command_name}")
            asyncio.run_coroutine_threadsafe(command_queue.put(command_name), loop)
        else:
            print(f"Unknown command: {command_name}")
    except Exception as e:
        print(f"Error: {e}")

def setup_mqtt():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC_COMMAND)
    client.on_message = on_message
    client.loop_start()
    return client

# Client MQTT pour envoyer les ACK
ack_client = mqtt.Client()
ack_client.connect(MQTT_BROKER, MQTT_PORT)
ack_client.loop_start()

def send_ack(command_name, status="received"):
    ack_payload = json.dumps({"command": command_name, "status": status})
    ack_client.publish(MQTT_TOPIC_ACK, ack_payload)
    print(f"ACK sent for command: {command_name} (status: {status})")

async def handle_commands():
    print("Ready to execute commands on Go2 (simulation).")
    while True:
        command_name = await command_queue.get()
        print(f"Executing command: {command_name} (ID: {SPORT_CMD[command_name]})")
        # Ici, tu appelles le robot réel
        await asyncio.sleep(2)  # Simulation d’exécution
        send_ack(command_name, "received")  # Publie l’ACK après exécution

if __name__ == "__main__":
    setup_mqtt()
    try:
        loop.run_until_complete(handle_commands())
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        ack_client.loop_stop()
        ack_client.disconnect()

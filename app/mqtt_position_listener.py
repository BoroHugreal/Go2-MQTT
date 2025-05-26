import threading
import paho.mqtt.client as mqtt
import json

# Variable globale pour stocker la dernière position et orientation reçues
last_position = {"x": 2.37556, "y": 48.77713, "yaw": 0}

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Position MQTT reçue : {payload}")
        last_position["x"] = payload.get("x", 0)
        last_position["y"] = payload.get("y", 0)
        # Ajoute la gestion de l’orientation
        if "yaw" in payload:
            last_position["yaw"] = payload.get("yaw", 0)
    except Exception as e:
        print(f"Erreur de décodage position: {e}")

def start_position_listener(broker, port, topic):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe(topic)
    client.loop_start()
    return client

def run_position_listener(broker, port, topic):
    thread = threading.Thread(target=start_position_listener, args=(broker, port, topic), daemon=True)
    thread.start()
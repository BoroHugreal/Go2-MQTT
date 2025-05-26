import threading
import paho.mqtt.client as mqtt

last_ack = {"command": None, "status": None}

def on_message(client, userdata, msg):
    import json
    payload = json.loads(msg.payload.decode())
    last_ack["command"] = payload.get("command")
    last_ack["status"] = payload.get("status")

def start_ack_listener(broker, port, topic):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe(topic)
    client.loop_start()
    return client

def run_listener(broker, port, topic):
    thread = threading.Thread(target=start_ack_listener, args=(broker, port, topic), daemon=True)
    thread.start()

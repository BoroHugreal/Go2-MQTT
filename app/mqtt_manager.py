# app/mqtt_manager.py
import threading
import paho.mqtt.client as mqtt
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD

class MQTTManager:
    def __init__(self):
        self.connected = False
        self.client = mqtt.Client()
        self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True

    def on_connect(self, client, userdata, flags, rc):
        self.connected = (rc == 0)
        print("[MQTT] Connecté" if self.connected else f"[MQTT] Connexion refusée (rc={rc})")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print("[MQTT] Déconnecté du broker")

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.thread.start()

    def _loop(self):
        self.client.loop_forever()

    def is_connected(self):
        return self.connected

    def publish(self, topic, payload):
        if self.connected:
            result = self.client.publish(topic, payload)
            return result.rc == 0
        else:
            print("[MQTT] Impossible de publier, non connecté.")
            return False

# Instance globale à importer partout
mqtt_manager = MQTTManager()
mqtt_manager.start()
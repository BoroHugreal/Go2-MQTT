# app/dev_tools.py
import paho.mqtt.client as mqtt
import json
import time
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD

# Dictionnaire des commandes sportives
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

class MQTTInspector:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.active = True

    def on_connect(self, client, userdata, flags, rc):
        print(f"\n✅ Connecté au broker MQTT (code {rc})")
        print("🔎 Écoute de tous les topics...")
        client.subscribe("#")  # S'abonner à tous les topics

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            try:
                # Essayer de parser le JSON pour un affichage structuré
                payload = json.loads(payload)
                payload_str = json.dumps(payload, indent=2)
            except:
                payload_str = payload
            
            # Décoder les commandes sportives si nécessaire
            if msg.topic == "robot/commands" and isinstance(payload, dict):
                cmd_code = payload.get("command")
                if isinstance(cmd_code, int):
                    cmd_name = next((k for k, v in SPORT_CMD.items() if v == cmd_code), "UNKNOWN_CMD")
                    payload_str = json.dumps({**payload, "command_name": cmd_name}, indent=2)
            
            print(f"\n📨 Topic: {msg.topic}")
            print(f"📝 Payload:\n{payload_str}")
            print("─" * 50)
        except Exception as e:
            print(f"Erreur de traitement: {e}")

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.loop_start()
        print("\n🚀 Démarrage de l'inspecteur MQTT...")
        print(f"🔌 Connexion à {MQTT_BROKER}:{MQTT_PORT}")
        print("📋 Commandes disponibles:")
        print("  'filter <topic>' - Filtrer un topic spécifique")
        print("  'clear' - Réinitialiser les filtres")
        print("  'exit' - Quitter\n")
        
        while self.active:
            command = input(">>> ").strip()
            if command.startswith("filter "):
                topic = command.split(" ", 1)[1]
                self.client.unsubscribe("#")
                self.client.subscribe(topic)
                print(f"🔍 Filtrage activé sur: {topic}")
            elif command == "clear":
                self.client.unsubscribe("#")
                self.client.subscribe("#")
                print("🔍 Filtrage désactivé")
            elif command == "exit":
                self.active = False

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("\n🛑 Inspecteur MQTT arrêté")

if __name__ == "__main__":
    inspector = MQTTInspector()
    try:
        inspector.start()
    except KeyboardInterrupt:
        pass
    finally:
        inspector.stop()
import paho.mqtt.client as mqtt
import json
import time

# Liste des points du chemin (latitude, longitude)
path = [
    (48.777164396, 2.375696799),
    (48.777266135, 2.375488087),
    (48.777245920, 2.375302510),
    (48.777219946, 2.374943893),
    (48.777252453, 2.375237042),
    (48.777247827, 2.375732456),
    (48.777378526, 2.375937183),
    (48.777426862, 2.376234988),
    (48.777376616, 2.376366631),
    (48.777280918, 2.376314928),
    (48.777184431, 2.376204572),
    (48.777053307, 2.376061392),
    (48.777101311, 2.375851686),
]

BROKER = "localhost"
PORT = 1883
TOPIC = "robot/position"

client = mqtt.Client()
client.connect(BROKER, PORT)
client.loop_start()

print("Simulation du déplacement du robot Go2 sur le chemin... (Ctrl+C pour arrêter)")

try:
    for lat, lon in path:
        pos = {"x": lon, "y": lat}
        client.publish(TOPIC, json.dumps(pos))
        print(f"Publié : {pos}")
        time.sleep(1)  # 1 seconde entre chaque point
    print("Chemin terminé !")
except KeyboardInterrupt:
    print("\nSimulation arrêtée.")
finally:
    client.loop_stop()
    client.disconnect()
# End of the simulation
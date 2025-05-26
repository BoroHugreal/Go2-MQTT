import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    print("Message received:", message.payload.decode())

client = mqtt.Client()
client.connect("localhost", 1883)
client.subscribe("robot/commands")
client.on_message = on_message
client.loop_forever()

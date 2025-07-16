import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("Cryptx/Private")

imagedata = ""

chunk_happen = False

def decompile_message():
    global imagedata

def read_message(client, userdata, message):
    global chunk_happen, imagedata

    msg = message.payload.decode()
    if msg == "chunk_start":
        print("chunk_start")
        chunk_happen = True
    if msg == "chunk_end":
        print("chunk_end")
        chunk_happen = False
        decompile_message()

    if chunk_happen and msg != "chunk_start" and msg != "chunk_end":
        imagedata += msg

def connect_message(client, userdata, flags, rc):
    print("Connected to Broker")


client.on_message = read_message
client.on_connect = connect_message

client.loop_forever()
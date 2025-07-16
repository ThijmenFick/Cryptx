import base64
import paho.mqtt.client as mqtt
import random
import string

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("Cryptx/Private")

imagedata = ""

chunk_happen = False

def xor_encrypt_decrypt(input_bytes: bytes, seed: str) -> bytes:
    random.seed(seed)
    return bytes(b ^ random.randint(0, 255) for b in input_bytes)

def decompile_filedata():
    global imagedata

    print("Received data")
    encrypted = base64.b64decode(imagedata)
    print("Decoded data")

    with open(f"{''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=20))}.enc", "wb") as out_file:
        out_file.write(encrypted)
    print("Written data to an encrypted file")

def read_message(client, userdata, message):
    global chunk_happen, imagedata

    msg = message.payload.decode()
    if msg == "chunk_start":
        print("chunk_start")
        chunk_happen = True
    if msg == "chunk_end" and chunk_happen:
        print("chunk_end")
        chunk_happen = False
        decompile_filedata()

    if chunk_happen and msg != "chunk_start" and msg != "chunk_end":
        imagedata += msg

def connect_message(client, userdata, flags, rc):
    print("Connected to Broker")


client.on_message = read_message
client.on_connect = connect_message

client.loop_forever()
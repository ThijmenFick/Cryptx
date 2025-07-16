import base64
import paho.mqtt.client as mqtt
import random
import string
from tqdm import tqdm

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("Cryptx/Private")

imagedata = ""
chunk_happen = False

filename = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=20))
file_extension = ""

def xor_encrypt_decrypt(input_bytes: bytes, seed: str) -> bytes:
    random.seed(seed)
    return bytes(b ^ random.randint(0, 255) for b in input_bytes)

def decompile_filedata():
    global imagedata

    print("Received data")

    encrypted = base64.b64decode(imagedata)
    print(imagedata)
    print(encrypted)
    print("Decoded data")

    with open("database.txt", "w") as datafile:
        datafile.write(f"F: {filename}, E: {file_extension}")

    with open(f"{filename}.enc", "wb") as out_file:
        out_file.write(encrypted)
    print("Written data to an encrypted file")

def read_message(client, userdata, message):
    msg = message.payload.decode()
    print(msg)
    if msg.startswith("up "):
        msg = msg.removeprefix("up ")
        global chunk_happen, imagedata

        if msg.startswith("chunk_start "):
            print("chunk_start")
            chunk_happen = True
            imagedata = ""
        if msg == "chunk_end" and chunk_happen:
            print("chunk_end")
            chunk_happen = False
            decompile_filedata()

        if chunk_happen and not msg.startswith("chunk_start ") and not msg.startswith("chunk_end "):
            print(msg)
            imagedata += msg

    if msg.startswith("dw "):
        msg = msg.removeprefix("dw ")
        print(msg)
        with open(msg, "rb") as file:
            file_content = file.read()
        converted_encrypted = base64.b64encode(file_content)
        print(f"Converted {len(file_content)} bytes to {len(converted_encrypted)} bytes with a ratio of {round(len(converted_encrypted) / len(file_content) * 100, 2)}%")

        client.publish("Cryptx/Private", "dwr chunk_start")
        chunks = [converted_encrypted[i:i + 1000] for i in range(0, len(converted_encrypted), 1000)]
        for chunk in tqdm(chunks, total=len(chunks), desc="Processing chunks"):
            client.publish("Cryptx/Private", "dwr " + chunk.decode("utf-8"))
        client.publish("Cryptx/Private", "dwr chunk_end")

def connect_message(client, userdata, flags, rc):
    print("Connected to Broker")


client.on_message = read_message
client.on_connect = connect_message

client.loop_forever()
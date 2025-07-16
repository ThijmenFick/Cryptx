import random
import base64
import string

import paho.mqtt.client as mqtt
from tqdm import tqdm

def xor_encrypt_decrypt(input_bytes: bytes, seed: str) -> bytes:
    random.seed(seed)
    return bytes(b ^ random.randint(0, 255) for b in input_bytes)

imagedata = ""
chunk_happen = False
def decompile_filedata():
    global imagedata

    print("Received data")
    missing_padding = len(imagedata) % 4
    if missing_padding != 0:
        imagedata += "=" * (4 - missing_padding)
    encrypted = base64.b64decode(imagedata)
    print("Decoded data")
    decrypted = xor_encrypt_decrypt(encrypted, "seed")
    print("Decrypted data")
    with open(f"{''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=20))}.jpg", "wb") as out_file: #change file type
        out_file.write(decrypted)
    print("Written data to an file")
def read_message(client, userdata, message):
    msg = message.payload.decode()
    if msg.startswith("dwr"):
        msg = msg.removeprefix("dwr ")
        global chunk_happen, imagedata

        if msg == "chunk_start":
            print("chunk_start")
            chunk_happen = True
            imagedata = ""
        if msg == "chunk_end" and chunk_happen:
            print("chunk_end")
            chunk_happen = False
            decompile_filedata()

        if chunk_happen and msg != "chunk_start" and msg != "chunk_end":
            imagedata += msg

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("Cryptx/Private")
client.on_message = read_message


option = input("UP/DW > ")

if option == "up":
    filename = input("Filename > ")

    with open(filename, "rb") as file:
        file_content = file.read()
        encrypted = xor_encrypt_decrypt(file_content, "seed")
    converted_encrypted = base64.b64encode(encrypted)

    print(f"Encrypted {len(file_content)} bytes to {len(encrypted)} bytes with a ratio of {round(len(encrypted) / len(file_content) * 100, 2)}%")
    print(f"Converted {len(encrypted)} bytes to {len(converted_encrypted)} bytes with a ratio of {round(len(converted_encrypted) / len(encrypted) * 100, 2)}%")
    print(f"Total Result of {len(file_content)} bytes to {len(converted_encrypted)} bytes with a ratio of {round(len(converted_encrypted) / len(file_content) * 100, 2)}%")

    client.publish("Cryptx/Private", "up chunk_start")
    chunks = [converted_encrypted[i:i + 1000] for i in range(0, len(converted_encrypted), 1000)]
    for chunk in tqdm(chunks, total=len(chunks), desc="Processing chunks"):
        client.publish("Cryptx/Private", "up " + chunk.decode("utf-8"))
    client.publish("Cryptx/Private", "up chunk_end")

if option == "dw":
    filename = input("Filename > ")
    client.publish("Cryptx/Private", "dw " + filename)

client.loop_forever()
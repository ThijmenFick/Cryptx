import random
import base64
import paho.mqtt.client as mqtt
from tqdm import tqdm

def xor_encrypt_decrypt(input_bytes: bytes, seed: str) -> bytes:
    random.seed(seed)
    return bytes(b ^ random.randint(0, 255) for b in input_bytes)


client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("Cryptx/Private")


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

    client.publish("Cryptx/Private", "chunk_start")
    chunks = [converted_encrypted[i:i + 1000] for i in range(0, len(converted_encrypted), 1000)]
    for chunk in tqdm(chunks, total=len(chunks), desc="Processing chunks"):
        client.publish("Cryptx/Private", chunk)
    client.publish("Cryptx/Private", "chunk_end")

client.loop_forever()
import hmac
import hashlib
import base64
import time
import urllib.parse
import json
import random
import paho.mqtt.client as mqtt

# Azure IoT Hub details (UPDATE THESE)
iot_hub_name = "ee5127iothub"  # Replace with your IoT Hub name
device_id = "feather-sense"      # Replace with your device ID
device_key = "2xrfxWY6jut7OCivCrJ628O2itUcAxZQ2M/jokt83rE="  # Replace with your Primary Key

# Function to generate SAS token
def generate_sas_token(uri, key, expiry=3600):
    ttl = int(time.time()) + expiry
    sign_key = f"{uri}\n{ttl}"
    signature = base64.b64encode(hmac.new(base64.b64decode(key), sign_key.encode('utf-8'), hashlib.sha256).digest()).decode()
    return f"SharedAccessSignature sr={uri}&sig={urllib.parse.quote(signature)}&se={ttl}"

# Generate SAS Token
resource_uri = f"{iot_hub_name}.azure-devices.net/devices/{device_id}"
sas_token = generate_sas_token(resource_uri, device_key)

# MQTT settings
broker = f"{iot_hub_name}.azure-devices.net"
port = 8883
mqtt_username = f"{iot_hub_name}.azure-devices.net/{device_id}/?api-version=2021-04-12"
topic = f"devices/{device_id}/messages/events/"

# Callback for successful connection
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to Azure IoT Hub! Sending data...")
    else:
        print(f"Failed to connect, return code {rc}")

# Set up MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=device_id, protocol=mqtt.MQTTv311)
client.username_pw_set(mqtt_username, sas_token)
client.tls_set()  # Enable TLS encryption
client.on_connect = on_connect

# Connect to Azure IoT Hub
client.connect(broker, port)

# Function to send telemetry data
def send_telemetry():
    while True:
        payload = {
            "Temperature": round(random.uniform(20.0, 30.0), 2),
            "Humidity": round(random.uniform(25.0, 35.0), 3),
            "Light": random.randint(400, 500),
            "CO2": round(random.uniform(700, 800), 2),
            "HumidityRatio": round(random.uniform(0.004, 0.005), 6),
            "Occupancy": random.choice([0, 1])
        }

        message = json.dumps(payload)
        client.publish(topic, message, qos=1)
        print(f"Sent message: {message}")
        
        time.sleep(5)  # Wait 5 seconds before sending the next message

# Start the loop in a non-blocking way
client.loop_start()

# Start sending data
send_telemetry()

"""
Azure IoT Hub MQTT Sender
-------------------------
A simple script to send simulated sensor data to Azure IoT Hub using MQTT protocol.
Great for educational purposes and basic IoT projects.
"""

import ssl
import time
import json
import base64
import hmac
import hashlib
import urllib.parse
import random
from datetime import datetime
from paho.mqtt import client as mqtt

# Azure IoT Hub connection parameters (replace with your values)
IOT_HUB_NAME = "ee5127iothub"
DEVICE_ID = "feather-sense"
DEVICE_KEY = "2xrfxWY6jut7OCivCrJ628O2itUcAxZQ2M/jokt83rE="
HOSTNAME = f"{IOT_HUB_NAME}.azure-devices.net"

# Topic to publish messages (IoT Hub format for device-to-cloud messages)
PUBLISH_TOPIC = f"devices/{DEVICE_ID}/messages/events/"

# How often to send data (in seconds)
SEND_INTERVAL = 5

def generate_sas_token(uri, key, expiry=3600):
    """
    Generate a SAS token for Azure IoT Hub authentication.
    
    Parameters:
        uri: The resource URI (typically the IoT Hub hostname)
        key: The device primary key (base64 encoded)
        expiry: Token expiry time in seconds (default: 1 hour)
        
    Returns:
        A SAS token string
    """
    # Calculate expiry time
    ttl = int(time.time()) + expiry
    sign_key = f"{urllib.parse.quote_plus(uri)}\n{ttl}"
    
    # Decode the device key (base64)
    key = base64.b64decode(key)
    
    # Create signature using HMAC-SHA256
    signature = base64.b64encode(
        hmac.HMAC(key, sign_key.encode('utf-8'), hashlib.sha256).digest()
    ).decode('utf-8')
    
    # Build the token
    token = {
        'sr': uri,
        'sig': signature,
        'se': str(ttl)
    }
    
    # Format as SharedAccessSignature string
    sas_token = 'SharedAccessSignature ' + urllib.parse.urlencode(token)
    
    print(f"Token will expire at: {datetime.fromtimestamp(ttl).strftime('%Y-%m-%d %H:%M:%S')}")
    return sas_token

def generate_sensor_data():
    """
    Generate simulated sensor data.
    
    Returns:
        A dictionary with random sensor values
    """
    data = {
        "Temperature": round(random.uniform(20.0, 25.0), 2),
        "Humidity": round(random.uniform(30.0, 60.0), 3),
        "Light": round(random.uniform(200, 800)),
        "CO2": round(random.uniform(400.0, 1000.0), 2),
        "HumidityRatio": round(random.uniform(0.002, 0.006), 6),
        "Occupancy": random.randint(0, 1)
    }
    return data

def on_connect(client, userdata, flags, rc, properties):
    """Callback function for when the client connects to the broker"""
    if rc == 0:
        print(f"Connected to Azure IoT Hub: {HOSTNAME}")
    else:
        print(f"Connection failed with code: {rc}")

def on_publish(client, userdata, mid, rc, properties):
    """Callback function for when a message is published"""
    print(f"Message {mid} published successfully")

def on_disconnect(client, userdata, flags, rc, properties):
    """Callback function for when the client disconnects"""
    if rc != 0:
        print(f"Unexpected disconnection, code: {rc}")
    else:
        print("Disconnected successfully")

def main():
    # Step 1: Generate SAS token for authentication
    resource_uri = f"{HOSTNAME}/devices/{DEVICE_ID}"
    sas_token = generate_sas_token(resource_uri, DEVICE_KEY)
    
    # Step 2: Create MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id = DEVICE_ID, protocol=mqtt.MQTTv311)
    
    # Step 3: Set up TLS for secure connection
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
    
    # Step 4: Set username and password
    # Note: Azure IoT Hub uses a specific format for the username
    username = f"{IOT_HUB_NAME}.azure-devices.net/{DEVICE_ID}/api-version=2018-06-30"
    client.username_pw_set(username, sas_token)
    
    # Step 5: Set up callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    try:
        # Step 6: Connect to Azure IoT Hub
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, port=8883, keepalive=60)
        
        # Step 7: Start the network loop
        client.loop_start()
        
        # Wait a moment to ensure connection is established
        time.sleep(1)
        
        print(f"\nSending simulated sensor data every {SEND_INTERVAL} seconds. Press Ctrl+C to exit.\n")
        message_counter = 1
        
        while True:
            # Generate simulated sensor data
            sensor_data = generate_sensor_data()
            payload = json.dumps(sensor_data)
            
            # Publish the message
            print(f"Sending message {message_counter}: {payload}")
            client.publish(PUBLISH_TOPIC, payload, qos=1)
            message_counter += 1
            
            # Wait for the next interval
            time.sleep(SEND_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nExiting program...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        client.loop_stop()
        client.disconnect()
        print("Disconnected and cleaned up")

if __name__ == "__main__":
    main()
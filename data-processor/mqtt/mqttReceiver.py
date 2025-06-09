import os
import json
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

class MQTTReceiver:
    def __init__(self, data_callback=None):
        self.data_callback = data_callback
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.setup_client()

    def setup_client(self):
        """Setup MQTT client with credentials and callbacks"""
        username = os.getenv("BROKER_USERNAME")
        password = os.getenv("BROKER_PASSWORD")
        
        if username and password:
            self.client.username_pw_set(username, password)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"MQTT Connected with result code {reason_code}")
        topic = os.getenv("MQTT_TOPIC", "weather/data")
        client.subscribe(topic, qos=1)
        print(f"Subscribed to topic: {topic}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            print(f"Received message on {msg.topic}: {payload}")
            
            # Call the callback function if provided
            if self.data_callback:
                self.data_callback(payload)
            else:
                print("⚠️ No data callback defined")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
        except Exception as e:
            print(f"❌ Error handling message: {e}")

    def on_disconnect(self, client, userdata, reason_code, properties):
        print(f"MQTT Disconnected with reason code: {reason_code}")

    def start_listening(self):
        """Start listening for MQTT messages"""
        endpoint = os.getenv("BROKER_ENDPOINT", "localhost")
        port = int(os.getenv("BROKER_PORT", "1883"))
        
        try:
            print(f"Connecting to MQTT broker at {endpoint}:{port}")
            self.client.connect(endpoint, port, 60)
            self.client.loop_forever()
        except Exception as e:
            print(f"❌ Failed to connect to MQTT broker: {e}")

# Legacy function for backward compatibility
def start_mqtt_listener():
    """Legacy function - use MQTTReceiver class instead"""
    print("⚠️ Using legacy MQTT listener - consider updating to use MQTTReceiver class")
    receiver = MQTTReceiver()
    receiver.start_listening()
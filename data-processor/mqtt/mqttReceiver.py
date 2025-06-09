import json
import paho.mqtt.client as mqtt

class MQTTReceiver:
    def __init__(self, data_callback=None, mqtt_config=None):
        self.data_callback = data_callback
        self.mqtt_config = mqtt_config or {}
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.setup_client()

    def setup_client(self):
        """Setup MQTT client with credentials and callbacks"""
        username = self.mqtt_config.get('username')
        password = self.mqtt_config.get('password')
        
        if username and password:
            self.client.username_pw_set(username, password)
            print(f"MQTT credentials set for user: {username}")
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"MQTT Connected with result code {reason_code}")
        topic = self.mqtt_config.get('topic', 'weather/data')
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
        endpoint = self.mqtt_config.get('endpoint', 'localhost')
        port = self.mqtt_config.get('port', 1883)
        
        try:
            print(f"Connecting to MQTT broker at {endpoint}:{port}")
            self.client.connect(endpoint, port, 60)
            self.client.loop_forever()
        except Exception as e:
            print(f"❌ Failed to connect to MQTT broker: {e}")
            raise

# Legacy function for backward compatibility
def start_mqtt_listener():
    """Legacy function - use MQTTReceiver class instead"""
    from config import Config
    print("⚠️ Using legacy MQTT listener - consider updating to use MQTTReceiver class")
    receiver = MQTTReceiver(mqtt_config=Config.get_mqtt_config())
    receiver.start_listening()
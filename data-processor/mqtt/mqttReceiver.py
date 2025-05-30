import os
import json
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from db.influxWriter import write_data

load_dotenv()

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"MQTT Connected with result code {reason_code}")
    client.subscribe("weather/data", qos=1)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"Received message on {msg.topic}: {payload}")

        from db.influxClient import connect_influxdb
        influx_client = connect_influxdb()
        write_data(
            client=influx_client,
            bucket=os.getenv("INFLUXDB_BUCKET"),
            measurement="weather_sensor",
            data=payload
        )
    except Exception as e:
        print(f"Error handling message: {e}")

def start_mqtt_listener():
    
    endpoint = os.getenv("BROKER_ENDPOINT")
    username = os.getenv("BROKER_USERNAME")
    password = os.getenv("BROKER_PASSWORD")
    
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    mqttc.username_pw_set(username, password)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect(endpoint, 1883, 60)
    mqttc.loop_forever()

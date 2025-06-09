import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # InfluxDB Configuration
    INFLUXDB_URL = os.getenv("INFLUXDB_URL")
    INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
    INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
    INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
    
    # MQTT Configuration
    MQTT_BROKER_ENDPOINT = os.getenv("BROKER_ENDPOINT")
    MQTT_BROKER_PORT = int(os.getenv("BROKER_PORT"))
    MQTT_BROKER_USERNAME = os.getenv("BROKER_USERNAME")
    MQTT_BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")
    MQTT_TOPIC = os.getenv("MQTT_TOPIC")
    
    # Data Configuration
    DATA_LOCATION = os.getenv("DATA_LOCATION", "unknown")
    MEASUREMENT_NAME = os.getenv("MEASUREMENT_NAME", "weather_sensor")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = [
            ('INFLUXDB_TOKEN', cls.INFLUXDB_TOKEN),
            ('INFLUXDB_ORG', cls.INFLUXDB_ORG),
            ('INFLUXDB_BUCKET', cls.INFLUXDB_BUCKET),
            ('MQTT_BROKER_PASSWORD', cls.MQTT_BROKER_PASSWORD)
        ]
        
        missing = [name for name, value in required_vars if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        
        return True
    
    @classmethod
    def get_influx_config(cls):
        """Get InfluxDB configuration as dict"""
        return {
            'url': cls.INFLUXDB_URL,
            'token': cls.INFLUXDB_TOKEN,
            'org': cls.INFLUXDB_ORG,
            'bucket': cls.INFLUXDB_BUCKET
        }
        
    @classmethod
    def get_mqtt_config(cls):
        """Get MQTT configuration as dict"""
        return {
            'endpoint': cls.MQTT_BROKER_ENDPOINT,
            'port': cls.MQTT_BROKER_PORT,
            'username': cls.MQTT_BROKER_USERNAME,
            'password': cls.MQTT_BROKER_PASSWORD,
            'topic': cls.MQTT_TOPIC
        }
    
    @classmethod
    def print_config_summary(cls, hide_secrets=True):
        """Print configuration summary for debugging"""
        return {
            'influx_url': cls.INFLUXDB_URL,
            'influx_org': cls.INFLUXDB_ORG,
            'influx_bucket': cls.INFLUXDB_BUCKET,
            'influx_token_set': bool(cls.INFLUXDB_TOKEN),
            'mqtt_endpoint': cls.MQTT_BROKER_ENDPOINT,
            'mqtt_port': cls.MQTT_BROKER_PORT,
            'mqtt_username': cls.MQTT_BROKER_USERNAME,
            'mqtt_password_set': bool(cls.MQTT_BROKER_PASSWORD),
            'mqtt_topic': cls.MQTT_TOPIC,
            'data_location': cls.DATA_LOCATION,
            'measurement_name': cls.MEASUREMENT_NAME
        }
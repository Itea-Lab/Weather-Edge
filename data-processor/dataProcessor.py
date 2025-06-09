import os
from dotenv import load_dotenv
from mqtt.mqttReceiver import MQTTReceiver
from db.influxClient import connect_influxdb
from db.influxWriter import write_data

load_dotenv()

class WeatherDataProcessor:
    def __init__(self):
        self.influx_client = None
        self.mqtt_receiver = None
        
        # InfluxDB Configuration
        self.influx_url = os.getenv("INFLUXDB_URL")
        self.influx_token = os.getenv("INFLUXDB_TOKEN")
        self.influx_org = os.getenv("INFLUXDB_ORG")
        self.influx_bucket = os.getenv("INFLUXDB_BUCKET")
        
        # Validate configuration
        self.validate_config()
        
        # Setup connections
        self.setup_influxdb()
        
    def validate_config(self):
        required_configs = {
            "INFLUXDB_TOKEN": self.influx_token,
            "INFLUXDB_ORG": self.influx_org,
            "INFLUXDB_BUCKET": self.influx_bucket
        }
        
        missing_configs = [key for key, value in required_configs.items() if not value]
        if missing_configs:
            raise ValueError(f"Missing required environment variables: {missing_configs}")
        
        print("✅ Configuration validated successfully")
        
    def setup_influxdb(self):
        """Initialize InfluxDB connection"""
        try:
            print(f"🔗 Connecting to InfluxDB at {self.influx_url}")
            self.influx_client = connect_influxdb(
                url=self.influx_url,
                token=self.influx_token,
                org=self.influx_org
            )
            if self.influx_client:
                print("✅ InfluxDB connection established")
            else:
                print("Error: Failed to connect to InfluxDB")
        except Exception as e:
            print(f"Error: Error setting up InfluxDB: {e}")
            raise
    
    def process_weather_data(self, data):
        """Process and store weather data received from MQTT"""
        try:
            print(f"Processing weather data: {data}")
            
            # Validate data structure
            if not self.validate_weather_data(data):
                print("Error: Invalid weather data format")
                return False
            
            # Write to InfluxDB
            if self.influx_client:
                success = write_data(
                    client=self.influx_client,
                    bucket=self.influx_bucket,
                    measurement="weather_sensor",
                    data=data
                )
                if success:
                    print("✅ Weather data successfully stored in InfluxDB")
                    return True
                else:
                    print("Error: Failed to store weather data in InfluxDB")
                    return False
            else:
                print("Error: InfluxDB client not available")
                return False
                
        except Exception as e:
            print(f"Error processing weather data: {e}")
            return False
    
    def validate_weather_data(self, data):
        """Validate weather data structure"""
        required_fields = [
            "Temperature", "Humidity", "Barometric Pressure",
            "Wind Direction", "Avg Wind Speed", "Max Wind Speed",
            "Rainfall (1hr)", "Rainfall (24hr)"
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"Error Missing required fields: {missing_fields}")
            return False
        return True
    
    def get_config_summary(self):
        """Return configuration summary for debugging"""
        return {
            "influx_url": self.influx_url,
            "influx_org": self.influx_org,
            "influx_bucket": self.influx_bucket,
            "influx_token_set": bool(self.influx_token)
        }
    
    def start_processing(self):
        """Start the data processing pipeline"""
        print("Starting Weather Data Processor...")
        print(f"Configuration: {self.get_config_summary()}")
        
        # Create MQTT receiver with callback
        self.mqtt_receiver = MQTTReceiver(data_callback=self.process_weather_data)

        print("Starting MQTT listener...")
        self.mqtt_receiver.start_listening()

if __name__ == "__main__":
    processor = WeatherDataProcessor()
    processor.start_processing()
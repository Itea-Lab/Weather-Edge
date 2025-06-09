import os
from config import Config
from mqtt.mqttReceiver import MQTTReceiver
from db.influxClient import connect_influxdb
from db.influxWriter import write_data

class WeatherDataProcessor:
    def __init__(self):
        self.influx_client = None
        self.mqtt_receiver = None
        
        # Validate configuration
        Config.validate()
        print("✅ Configuration validated successfully")
        
        # Get configurations from centralized Config
        self.influx_config = Config.get_influx_config()
        self.mqtt_config = Config.get_mqtt_config()
        
        # Setup connections
        self.setup_influxdb()
        
    def setup_influxdb(self):
        """Initialize InfluxDB connection"""
        try:
            print(f"Connecting to InfluxDB at {self.influx_config['url']}")
            self.influx_client = connect_influxdb(
                url=self.influx_config['url'],
                token=self.influx_config['token'],
                org=self.influx_config['org']
            )
            if self.influx_client:
                print("✅ InfluxDB connection established")
            else:
                print("❌ Failed to connect to InfluxDB")
        except Exception as e:
            print(f"❌ Error setting up InfluxDB: {e}")
            raise
    
    def process_weather_data(self, data):
        """Process and store weather data received from MQTT"""
        try:
            print(f"Processing weather data: {data}")
            
            # Validate data structure
            if not self.validate_weather_data(data):
                print("⚠️ Invalid weather data format")
                return False
            
            # Write to InfluxDB
            if self.influx_client:
                success = write_data(
                    client=self.influx_client,
                    bucket=self.influx_config['bucket'],
                    measurement=Config.MEASUREMENT_NAME,
                    data=data,
                    location=Config.DATA_LOCATION
                )
                if success:
                    print("✅ Weather data successfully stored in InfluxDB")
                    return True
                else:
                    print("❌ Failed to store weather data in InfluxDB")
                    return False
            else:
                print("❌ InfluxDB client not available")
                return False
                
        except Exception as e:
            print(f"❌ Error processing weather data: {e}")
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
            print(f"⚠️ Missing required fields: {missing_fields}")
            return False
        return True
    
    # def get_config_summary(self):
    #     return Config.print_config_summary()
    
    def start_processing(self):
        """Start the data processing pipeline"""
        print("Starting Weather Data Processing pipepline...")
        # -------------------------------------------------
        # FOR DEBUGGING PURPOSES: ONLY USE WHEN YOU WANT TO CHECK CONFIGURATION
        # -------------------------------------------------
        # print("Configuration Summary:")
        # config_summary = self.get_config_summary()
        # for key, value in config_summary.items():
        #     print(f"   {key}: {value}")
        
        # Create MQTT receiver with callback and config
        self.mqtt_receiver = MQTTReceiver(
            data_callback=self.process_weather_data,
            mqtt_config=self.mqtt_config
        )
        
        # Start listening for MQTT messages
        print("Starting MQTT listener...")
        self.mqtt_receiver.start_listening()

if __name__ == "__main__":
    processor = WeatherDataProcessor()
    processor.start_processing()
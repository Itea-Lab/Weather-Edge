import os
from config import Config
from mqtt.mqttReceiver import MQTTReceiver
from mqtt.mqttPublisher import AWSIoTPublisher
from db.influxClient import connect_influxdb
from db.influxWriter import write_data

class WeatherDataProcessor:
    def __init__(self):
        self.influx_client = None
        self.mqtt_receiver = None
        self.aws_publisher = None
        
        # Validate configuration
        Config.validate()
        print("✅ Configuration validated successfully")
        
        # Get configurations from centralized Config
        self.influx_config = Config.get_influx_config()
        self.mqtt_config = Config.get_mqtt_config()
        
        # Setup connections
        self.setup_influxdb()
        self.setup_aws_iot()
        
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
    
    def setup_aws_iot(self):
        """Initialize AWS IoT connection"""
        try:
            print("Setting up AWS IoT connection...")
            self.aws_publisher = AWSIoTPublisher(credentials_dir="credentials")
            
            if self.aws_publisher.connect():
                print("✅ AWS IoT connection established")
            else:
                print("❌ Failed to connect to AWS IoT (will continue without cloud publishing)")
                self.aws_publisher = None
        except Exception as e:
            print(f"⚠️ AWS IoT setup failed (will continue without cloud publishing): {e}")
            self.aws_publisher = None
    
    def process_weather_data(self, data):
        """Process and store weather data received from MQTT"""
        try:
            print(f"Processing weather data: {data}")
            
            # Validate data structure
            if not self.validate_weather_data(data):
                print("⚠️ Invalid weather data format")
                return False
            
            # Initialize success flags
            influx_success = False
            aws_success = False
            
            # Write to InfluxDB
            if self.influx_client:
                influx_success = write_data(
                    client=self.influx_client,
                    bucket=self.influx_config['bucket'],
                    measurement=Config.MEASUREMENT_NAME,
                    data=data,
                    location=Config.DATA_LOCATION
                )
                if influx_success:
                    print("✅ Weather data successfully stored in InfluxDB")
                else:
                    print("❌ Failed to store weather data in InfluxDB")
            else:
                print("❌ InfluxDB client not available")
            
            # Publish to AWS IoT Cloud
            if self.aws_publisher:
                # Check connection and attempt reconnect if needed
                if not self.aws_publisher.is_connection_healthy():
                    print("🔄 AWS IoT connection lost, attempting reconnect...")
                    try:
                        # Add a small delay before reconnecting
                        import time
                        time.sleep(2)
                        
                        if self.aws_publisher.connect():
                            print("✅ AWS IoT reconnected successfully")
                        else:
                            print("❌ AWS IoT reconnection failed")
                    except Exception as e:
                        print(f"❌ AWS IoT reconnection error: {e}")
                
                # Try to publish if connected
                if self.aws_publisher.is_connection_healthy():
                    aws_success = self.aws_publisher.publish_weather_data(
                        weather_data=data,
                        location=Config.DATA_LOCATION
                    )
                    if aws_success:
                        print("✅ Weather data successfully published to AWS IoT")
                    else:
                        print("❌ Failed to publish weather data to AWS IoT")
                else:
                    print("⚠️ AWS IoT connection unavailable, skipping cloud publish")
            else:
                print("⚠️ AWS IoT publisher not initialized, skipping cloud publish")
            
            # Return True if at least one destination succeeded
            overall_success = influx_success or aws_success
            if overall_success:
                print("✅ Weather data processing completed successfully")
            else:
                print("❌ All data storage/publishing attempts failed")
            
            return overall_success
                
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
    
    def get_config_summary(self):
        return Config.print_config_summary()
    
    def start_processing(self):
        """Start the data processing pipeline"""
        print("Starting Weather Data Processing Pipeline...")
        print("Configuration Summary:")
        config_summary = self.get_config_summary()
        for key, value in config_summary.items():
            print(f"   {key}: {value}")
        
        try:
            # Create MQTT receiver with callback and config
            self.mqtt_receiver = MQTTReceiver(
                data_callback=self.process_weather_data,
                mqtt_config=self.mqtt_config
            )
            
            # Start listening for MQTT messages
            print("Starting MQTT listener...")
            self.mqtt_receiver.start_listening()
            
        except KeyboardInterrupt:
            print("\n---Shutdown signal received...---")
            self.shutdown()
        except Exception as e:
            print(f"❌ Error in processing pipeline: {e}")
            self.shutdown()
            raise
    
    def shutdown(self):
        """Gracefully shutdown all connections"""
        print("Shutting down connections...")
        
        # Disconnect AWS IoT
        if self.aws_publisher:
            self.aws_publisher.disconnect()
        
        # Close InfluxDB connection
        if self.influx_client:
            try:
                self.influx_client.close()
                print("✅ InfluxDB connection closed")
            except Exception as e:
                print(f"⚠️ Error closing InfluxDB: {e}")
        
        print("✅ Shutdown complete")

if __name__ == "__main__":
    processor = WeatherDataProcessor()
    processor.start_processing()
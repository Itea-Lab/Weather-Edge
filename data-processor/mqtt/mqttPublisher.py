#!/usr/bin/env python3
import time
import json
import os
from datetime import datetime
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import threading

class AWSIoTPublisher:
    def __init__(self, credentials_dir="credentials"):
        """
        Initialize AWS IoT Publisher
        Args:
            credentials_dir: Directory containing AWS IoT credentials
        """
        self.credentials_dir = credentials_dir
        self.connection = None
        self.is_connected = False
        self.publish_count = 0
        self.connection_lock = threading.Lock()
        
        # Device-specific attributes (will be set by load_aws_config)
        self.device_name = None
        self.client_id = None
        self.endpoint = None
        self.port = None
        self.publish_topic = None
        self.cert_path = None
        self.private_key_path = None
        self.ca_path = None
        
        # Load configuration from connection info
        self.load_aws_config()
        
    def load_aws_config(self):
        """Load AWS IoT configuration from credentials directory"""
        try:
            # Discover certificate files dynamically
            cert_files = self._discover_certificate_files()
            
            # Load connection info
            connection_info_path = cert_files['connection_info']
            with open(connection_info_path, 'r') as f:
                config = json.load(f)
            
            self.endpoint = config['endpoint']
            self.port = config.get('port', 8883)
            
            # Handle dynamic topic with DATA_LOCATION placeholder
            topic_template = config['topics']['publish']
            self.topic_template = topic_template
            
            # Get DATA_LOCATION from environment
            data_location = os.getenv('DATA_LOCATION', 'unknown')
            
            # If topic template doesn't have {DATA_LOCATION}, append it
            if '{DATA_LOCATION}' not in topic_template:
                # Append the data location to make it dynamic
                self.publish_topic = f"{topic_template}/{data_location}"
                self.topic_template = f"{topic_template}/{{DATA_LOCATION}}"
                print(f"Enhanced topic from '{topic_template}' to '{self.publish_topic}'")
            else:
                # Replace {DATA_LOCATION} with actual value
                self.publish_topic = topic_template.replace('{DATA_LOCATION}', data_location)
            
            self.data_location = data_location
            
            # Set certificate paths from discovered files
            self.cert_path = cert_files['certificate']
            self.private_key_path = cert_files['private_key']
            self.ca_path = cert_files['ca_cert']
            
            # Extract device name from certificate filename
            cert_filename = os.path.basename(self.cert_path)
            self.device_name = cert_filename.replace('_certificate.pem', '')
            self.client_id = f"{self.device_name}-weather-edge"
            
            # Download Amazon Root CA if not exists
            if not os.path.exists(self.ca_path):
                print("Amazon Root CA not found, downloading...")
                self._download_amazon_root_ca()
            
            print(f"AWS IoT Config loaded:")
            print(f"   Device: {self.device_name}")
            print(f"   Client ID: {self.client_id}")
            print(f"   Endpoint: {self.endpoint}")
            print(f"   Topic Template: {self.topic_template}")
            print(f"   Resolved Topic: {self.publish_topic}")
            print(f"   Data Location: {data_location}")
            
        except Exception as e:
            print(f"❌ Failed to load AWS config: {e}")
            raise
    
    def _discover_certificate_files(self):
        """Discover certificate files dynamically based on patterns"""
        if not os.path.exists(self.credentials_dir):
            raise FileNotFoundError(f"Credentials directory not found: {self.credentials_dir}")
        
        files = os.listdir(self.credentials_dir)
        cert_files = {}
        
        # Find connection info file (*_connection_info.json)
        connection_files = [f for f in files if f.endswith('_connection_info.json')]
        if not connection_files:
            raise FileNotFoundError("No connection info file (*_connection_info.json) found in credentials directory")
        
        if len(connection_files) > 1:
            print(f"⚠️ Multiple connection info files found, using: {connection_files[0]}")
        
        connection_file = connection_files[0]
        cert_files['connection_info'] = os.path.join(self.credentials_dir, connection_file)
        
        # Extract device name from connection info filename
        device_name = connection_file.replace('_connection_info.json', '')
        
        # Find certificate file (*_certificate.pem)
        cert_pattern = f"{device_name}_certificate.pem"
        cert_path = os.path.join(self.credentials_dir, cert_pattern)
        if not os.path.exists(cert_path):
            # Try to find any certificate file
            cert_files_found = [f for f in files if f.endswith('_certificate.pem')]
            if not cert_files_found:
                raise FileNotFoundError("No certificate file (*_certificate.pem) found")
            cert_pattern = cert_files_found[0]
            cert_path = os.path.join(self.credentials_dir, cert_pattern)
            print(f"⚠️ Using certificate file: {cert_pattern}")
        
        cert_files['certificate'] = cert_path
        
        # Find private key file (*_private_key.pem)
        key_pattern = f"{device_name}_private_key.pem"
        key_path = os.path.join(self.credentials_dir, key_pattern)
        if not os.path.exists(key_path):
            # Try to find any private key file
            key_files_found = [f for f in files if f.endswith('_private_key.pem')]
            if not key_files_found:
                raise FileNotFoundError("No private key file (*_private_key.pem) found")
            key_pattern = key_files_found[0]
            key_path = os.path.join(self.credentials_dir, key_pattern)
            print(f"⚠️ Using private key file: {key_pattern}")
        
        cert_files['private_key'] = key_path
        
        # Set Amazon Root CA path
        cert_files['ca_cert'] = os.path.join(self.credentials_dir, "AmazonRootCA1.pem")
        
        print(f"Found certificate files:")
        print(f"   Connection Info: {os.path.basename(cert_files['connection_info'])}")
        print(f"   Certificate: {os.path.basename(cert_files['certificate'])}")
        print(f"   Private Key: {os.path.basename(cert_files['private_key'])}")
        print(f"   CA Certificate: {os.path.basename(cert_files['ca_cert'])}")
        
        return cert_files
    
    def _download_amazon_root_ca(self):
        """Download Amazon Root CA certificate"""
        import urllib.request
        
        ca_url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
        
        try:
            print(f"Downloading Amazon Root CA from {ca_url}")
            urllib.request.urlretrieve(ca_url, self.ca_path)
            print(f"✅ Downloaded Amazon Root CA to {self.ca_path}")
        except Exception as e:
            print(f"⚠️ Failed to download Amazon Root CA: {e}")
            print("   Will attempt connection without CA file")
            self.ca_path = None
    
    def validate_certificates(self):
        """Validate that certificate files exist"""
        files_to_check = [
            (self.cert_path, "Device certificate"),
            (self.private_key_path, "Private key"),
        ]
        
        missing_files = []
        for file_path, description in files_to_check:
            if not os.path.exists(file_path):
                missing_files.append(f"{description}: {file_path}")
        
        if missing_files:
            print("❌ Missing certificate files:")
            for missing in missing_files:
                print(f"  - {missing}")
            return False
        
        print("✅ All certificate files found.")
        return True
    
    def on_connection_interrupted(self, connection, error, **kwargs):
        # AWS IoT connections can be interrupted normally, so just log and update state
        print(f"AWS IoT connection interrupted, will auto-reconnect: {error}")
        with self.connection_lock:
            self.is_connected = False
    
    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        print(f"✅ AWS IoT connection resumed. Return code: {return_code}")
        with self.connection_lock:
            self.is_connected = True
    
    def on_connection_success(self, connection, callback_data):
        print(f"✅ AWS IoT connected successfully!")
        with self.connection_lock:
            self.is_connected = True
    
    def on_connection_failure(self, connection, callback_data):
        print(f"❌ AWS IoT connection failed: {callback_data.error}")
        with self.connection_lock:
            self.is_connected = False
    
    def on_connection_closed(self, connection, callback_data):
        print("---AWS IoT connection closed---")
        with self.connection_lock:
            self.is_connected = False
    
    def on_publish_complete(self, future):
        """Callback for when publish completes"""
        try:
            future.result()  # This will raise an exception if publish failed
            self.publish_count += 1
            print(f"✅ AWS IoT publish {self.publish_count} completed successfully")
        except Exception as e:
            print(f"❌ AWS IoT publish failed: {e}")
    
    def connect(self):
        """Establish connection to AWS IoT Core"""
        if not self.validate_certificates():
            raise Exception("Certificate validation failed")
        
        try:
            print("Creating AWS IoT MQTT connection...")
            
            # Create the MQTT connection with improved stability settings
            self.connection = mqtt_connection_builder.mtls_from_path(
                endpoint=self.endpoint,
                port=self.port,
                cert_filepath=self.cert_path,
                pri_key_filepath=self.private_key_path,
                ca_filepath=self.ca_path if self.ca_path and os.path.exists(self.ca_path) else None,
                client_id=self.client_id,
                clean_session=False,
                keep_alive_secs=60,  # Increased from 30 to 60 seconds
                ping_timeout_ms=30000,  # 30 second ping timeout
                protocol_operation_timeout_ms=60000,  # 60 second operation timeout
                on_connection_interrupted=self.on_connection_interrupted,
                on_connection_resumed=self.on_connection_resumed,
                on_connection_success=self.on_connection_success,
                on_connection_failure=self.on_connection_failure,
                on_connection_closed=self.on_connection_closed
            )
            
            print(f"Connecting to AWS IoT at {self.endpoint}...")
            connect_future = self.connection.connect()
            connect_future.result(timeout=10)
            
            # Wait for connection to stabilize
            time.sleep(2)
            
            if self.is_connected:
                print("✅ AWS IoT connection established!")
                return True
            else:
                print("❌ AWS IoT connection failed")
                return False
                
        except Exception as e:
            print(f"❌ AWS IoT connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from AWS IoT Core"""
        if self.connection and self.is_connected:
            try:
                print("---Disconnecting from AWS IoT...---")
                disconnect_future = self.connection.disconnect()
                disconnect_future.result(timeout=5)
                print("✅ AWS IoT disconnected successfully!")
            except Exception as e:
                print(f"❌ Error during AWS IoT disconnect: {e}")
    
    def publish_weather_data(self, weather_data, location="unknown"):
        """
        Publish weather data to AWS IoT Core
        Args:
            weather_data: Dict containing weather sensor data
            location: Location identifier
        """
        if not self.is_connected:
            print("⚠️ AWS IoT not connected, skipping publish")
            return False
        
        try:
            # Prepare the message payload
            message = {
                "deviceId": self.client_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "location": location,
                "data": {
                    "temperature": float(weather_data.get("Temperature", 0)),
                    "humidity": float(weather_data.get("Humidity", 0)),
                    "pressure": float(weather_data.get("Barometric Pressure", 0)),
                    "windDirection": int(weather_data.get("Wind Direction", 0)),
                    "avgWindSpeed": float(weather_data.get("Avg Wind Speed", 0)),
                    "maxWindSpeed": float(weather_data.get("Max Wind Speed", 0)),
                    "rainfall1hr": float(weather_data.get("Rainfall (1hr)", 0)),
                    "rainfall24hr": float(weather_data.get("Rainfall (24hr)", 0))
                },
                "metadata": {
                    "source": "weather-edge-processor",
                    "version": "1.0",
                    "publishCount": self.publish_count + 1
                }
            }
            
            message_json = json.dumps(message, indent=2)
            
            print(f"Publishing to AWS IoT topic: {self.publish_topic}")
            print(f"Weather data: Temperature={weather_data.get('Temperature')}°C, Humidity={weather_data.get('Humidity')}%")
            
            # Publish to AWS IoT
            publish_result = self.connection.publish(
                topic=self.publish_topic,
                payload=message_json,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            
            # Handle different return types
            if isinstance(publish_result, tuple):
                publish_future, packet_id = publish_result
                print(f"  → Packet ID: {packet_id}")
            else:
                publish_future = publish_result
            
            # Add completion callback
            if hasattr(publish_future, 'add_done_callback'):
                publish_future.add_done_callback(self.on_publish_complete)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to publish to AWS IoT: {e}")
            return False
    
    def is_connection_healthy(self):
        """Check if connection is healthy and still active"""
        with self.connection_lock:
            if not self.is_connected or self.connection is None:
                return False
            
            # Additional check - if we've had recent interruptions, consider unhealthy
            try:
                # The connection object should have some indication of its state
                # For now, just return the basic connection status
                return self.is_connected
            except Exception as e:
                print(f"⚠️ Error checking connection health: {e}")
                return False


# Legacy function for backward compatibility
def publish_to_aws(weather_data, location="unknown"):
    """
    Legacy function to publish weather data to AWS IoT
    Note: This creates a new connection each time, which is inefficient
    """
    print("⚠️ Using legacy AWS IoT publisher - consider using AWSIoTPublisher class")
    
    try:
        publisher = AWSIoTPublisher()
        if publisher.connect():
            result = publisher.publish_weather_data(weather_data, location)
            publisher.disconnect()
            return result
        return False
    except Exception as e:
        print(f"❌ Legacy AWS IoT publish failed: {e}")
        return False
# Weather Edge Configuration

Clone this repository to your edge device (Raspberry Pi, Ubuntu, Debian are supported)

```bash
git clone https://github.com/Itea-Lab/Weather-Edge.git
cd Weather-Edge
```

## Initial Setup

### 1. Create Environment Configuration File

Create a `.env` file in the project root to store all necessary credentials:

```bash
sudo nano .env
```

### 2. Environment Configuration Template

```env
# InfluxDB Configuration
INFLUXDB_USERNAME=<username>
INFLUXDB_PASSWORD=your_password
INFLUXDB_ORG=weather_org
INFLUXDB_BUCKET=weather_data
# For Docker containers, use service name
INFLUXDB_ROUTE=http://database:8086
# Token will be obtained after InfluxDB initialization (see step 6)
INFLUXDB_TOKEN=<your_token_here>

# Data Configuration
DATA_LOCATION=<your_location_name> (district1, district2, etc)
MEASUREMENT_NAME=weather_sensor

# MQTT Configuration
MQTT_PUB=espclient
SUB_USERNAME=raspiclient
MQTT_PASSWORD=your_mqtt_password
MQTT_TOPIC=weather/data
MQTT_PORT=1883
BROKER_ENDPOINT=mosquitto

# Dashboard Configuration
JWT_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
JWT_EXPIRES_IN=1d
ADMIN_USERNAME=admin
ADMIN_NAME=Administrator
ADMIN_PASSWORD_HASH=your_password_hash_here
ADMIN_EMAIL=admin@example.com
ADMIN_ROLE=admin
TEST_USERNAME=testuser
TEST_NAME=Test User
TEST_PASSWORD_HASH=your_password_hash_here
TEST_EMAIL=test@example.com
TEST_ROLE=user
```

### 3. Project Structure

```
weather-edge-config/
├── .env                       # Main environment variables
├── docker-compose.yml         # Docker services configuration
├── README.md
├── mosquitto-init/            # MQTT broker initialization
│   └── entrypoint.sh
├── mosquitto-config/          # MQTT broker config (auto-generated)
├── influxdb2-config/          # InfluxDB config (auto-generated)
├── influxdb2-data/            # InfluxDB data (auto-generated)
└── data-processor/
    ├── .env                   # Processor-specific env FOR LOCAL TESTING (copy of main .env)
    ├── credentials/           # Device certificates and keys (See step 4)
    ├── Dockerfile
    ├── requirements.txt
    ├── run.py                 # Application entry point
    ├── dataProcessor.py       # Main processing controller
    ├── config/
    │   ├── __init__.py
    │   └── config.py          # Centralized configuration
    ├── mqtt/
    │   ├── mqttReceiver.py    # MQTT message receiver
    │   └── mqttPublisher.py   # MQTT message publisher
    └── db/
        ├── influxClient.py    # InfluxDB connection management
        └── influxWriter.py    # Data writing operations
```

## Deployment Steps

### 4. Device Registration and AWS IoT Certificates

Before running the weather edge processor, you must register your device with the Weather Platform to obtain AWS IoT certificates:

#### 4.1. Device Registration Process

1. **Contact Weather Platform Administrator** or access the device registration portal
2. **Provide Device Information:**

   - Device name/identifier (e.g., `raspi-1`, `weather-station-01`)
   - Location/district assignment (e.g., `district5`, `station_01`)
   - Device type: Weather Edge Processor

3. **Receive Certificate Package:**
   You will receive a package containing:
   - `{device-name}_certificate.pem` - Device certificate
   - `{device-name}_private_key.pem` - Private key
   - `{device-name}_public_key.pem` - Public key (optional)
   - `{device-name}_connection_info.json` - Connection configuration
   - `AmazonRootCA1.pem` - Root CA certificate

#### 4.2. Certificate Installation

1. **Create credentials directory:**

   ```bash
   mkdir -p data-processor/credentials
   ```

2. **Copy certificate files:**
   Place all received certificate files in `data-processor/credentials/`:

   ```
   data-processor/credentials/
   ├── raspi-1_certificate.pem
   ├── raspi-1_private_key.pem
   ├── raspi-1_public_key.pem
   ├── raspi-1_connection_info.json
   └── AmazonRootCA1.pem
   ```

3. **Verify connection info format:**
   The `connection_info.json` should contain:

   ```json
   {
     "endpoint": "your-iot-endpoint.iot.us-east-1.amazonaws.com",
     "port": 8883,
     "topics": {
       "publish": "weatherPlatform/telemetry"
     }
   }
   ```

4. **Set proper permissions:**
   ```bash
   chmod 600 data-processor/credentials/*_private_key.pem
   chmod 644 data-processor/credentials/*.pem
   chmod 644 data-processor/credentials/*.json
   ```

#### 4.3. Configuration Verification

- Ensure `DATA_LOCATION` in your `.env` file matches your registered location
- The system will automatically discover certificate files based on naming patterns
- Dynamic topic routing will append your location to create: `weatherPlatform/telemetry/{DATA_LOCATION}`

### 5. Initial Docker Compose Setup
Enable execute permission for script file
```
chmod +x mosquitto-init/entrypoint.sh
```

Start the services for the first time:

```bash
docker compose up --build -d
```

### 6. InfluxDB Token Setup (IMPORTANT)

After the initial startup, you need to obtain the InfluxDB token:

1. **Access InfluxDB Web Interface:**

   ```
   http://localhost:8086
   ```

2. **Initial Setup:**

   - Username: Use `INFLUXDB_USERNAME` from your .env
   - Password: Use `INFLUXDB_PASSWORD` from your .env
   - Organization: Use `INFLUXDB_ORG` from your .env
   - Bucket: Use `INFLUXDB_BUCKET` from your .env

3. **Get API Token:**

   - Navigate to "Data" → "API Tokens"
   - Click "Generate API Token" → "All Access API Token"
   - Copy the generated token

4. **Update Environment Files:**
   Update both `.env` files with the token:

   ```env
   INFLUXDB_TOKEN=your_copied_token_here
   ```

5. **Restart Services:**
   ```bash
   docker compose down
   docker compose up -d
   ```

### 7. MQTT Broker Configuration

The MQTT broker supports two authentication modes:

#### Option A: Anonymous Access (Development)

Edit `mosquitto-config/mosquitto.conf` and set:

```
allow_anonymous true
```

#### Option B: User Authentication (Production - Recommended)

The system automatically creates authentication files:

- `mosquitto-config/passwd` - Stores username/password pairs
- `mosquitto-config/mosquitto.acl` - Access control list

**Default Users Created:**

- `espclient` - Can publish (write) to all topics
- `raspiclient` - Can subscribe (read) from all topics

**Testing MQTT Connection:**

Without authentication:

```bash
mosquitto_sub -h localhost -p 1883 -t weather/data
# Returns: Connection error: Connection Refused: not authorised.
```

With authentication:

```bash
mosquitto_sub -h localhost -p 1883 -u raspiclient -P your_mqtt_password -t weather/data
```

### 8. Running the Weather Data Processor

The data processor automatically:

- Connects to InfluxDB using the configured token
- Subscribes to MQTT topics for weather data
- Processes and stores incoming data
- Validates data format and handles errors

**Manual Testing:**

```bash
cd data-processor
python run.py
```

**Production (Docker):**
The processor runs automatically as part of the Docker Compose stack.

## Accessing Services

- **InfluxDB UI:** http://localhost:8086
- **Dashboard:** http://localhost:3000 (if enabled)
- **MQTT Broker:** localhost:1883

## Configuration Variables Reference

| Variable           | Purpose                   | Example                                   |
| ------------------ | ------------------------- | ----------------------------------------- |
| `INFLUXDB_TOKEN`   | Database API access       | `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` |
| `MQTT_PUB`     | MQTT publisher username  | `espclient`                             |
| `SUB_USERNAME`     | MQTT subscriber username  | `raspiclient`                             |
| `BROKER_ENDPOINT`  | MQTT broker address       | Raspi's IP address        |
| `DATA_LOCATION`    | Sensor location tag       | `district5`, `station_01`                 |
| `MEASUREMENT_NAME` | InfluxDB measurement name | `weather_sensor`                          |

## Troubleshooting

### Common Issues:

1. **AWS IoT Certificate Issues:**

   - **Missing certificates:** Ensure all certificate files are in `data-processor/credentials/`
   - **Permission denied:** Check file permissions (private keys should be 600)
   - **Connection refused:** Verify device is registered and certificates are valid
   - **Topic permission denied:** Ensure AWS IoT policy allows publishing to `weatherPlatform/telemetry/*`

2. **"Not authorized" MQTT error:**

   - Check username/password in .env
   - Verify ACL permissions
   - Ensure user exists in passwd file

3. **InfluxDB connection failed:**

   - Verify INFLUXDB_TOKEN is correct
   - Check if InfluxDB service is running
   - Validate organization and bucket names

4. **Environment variables not loading:**
   - Ensure .env file exists in correct location
   - Check for typos in variable names
   - Restart containers after changes

### Debug Commands:

```bash
# Check container status
docker compose ps

# View logs
docker compose logs weather-edge-processor
docker compose logs database
docker compose logs mosquitto

# Test MQTT connectivity
docker exec -it mqtt-broker mosquitto_sub -h localhost -u raspiclient -P your_password -t weather/data

# Test AWS IoT certificate discovery
cd data-processor
python -c "from mqtt.mqttPublisher import AWSIoTPublisher; pub = AWSIoTPublisher(); print('Certificates discovered successfully')"

# Verify certificate files
ls -la data-processor/credentials/
```

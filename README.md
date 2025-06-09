# Setup Weather Edge
Clone this repo to your Raspberry Pi (Debian, Ubuntu are ok)  
```
git clone https://github.com/Itea-Lab/Weather-Edge.git
cd Weather-Edge
```

### Create an .env file to store necessary credentials 
`sudo nano .env`

```
# InfluxDB credentials
INFLUXDB_USERNAME=<influx_username>
INFLUXDB_PASSWORD=<influx_password>
INFLUXDB_ORG=<influx_org>
INFLUXDB_BUCKET=<influx_bucket_name>
# If you are running InfluxDB in a different container, use the service name as the route
INFLUXDB_ROUTE=http://<service_name>:8086
INFLUXDB_TOKEN=<your_influxdb_token>
# MQTT credentials
MQTT_PUB=espclient
MQTT_SUB=rapiclient
MQTT_PASSWORD=<your_mqtt_password>
MQTT_TOPIC=<your_mqtt_topic>
#Dashboard
JWT_SECRET=<your_jwt_secret>
JWT_EXPIRES_IN=<duration>
ADMIN_USERNAME=<admin_username>
ADMIN_NAME=<admin_name>
ADMIN_PASSWORD_HASH=<password_hash>
ADMIN_EMAIL=<admin_email>
ADMIN_ROLE="admin"
TEST_USERNAME=<test_username>
TEST_NAME=<test_name>
TEST_PASSWORD_HASH=<password_hash>
TEST_EMAIL=test@example.com
TEST_ROLE="user"
```

### Folder structure
```
data-processor/
├── dataProcessor.py          # Main processing script (centralized controller)
├── run.py                    # Main runner
├── requirements.txt
├── Dockerfile
├── .env
├── config/                   # Configuration module
│   └── settings.py
├── mqtt/
│   ├── mqttReceiver.py      # Updated MQTT receiver with callback support
│   └── mqttPublisher.py
├── db/
│   ├── influxClient.py
│   └── influxWriter.py
└── data_filtering/          # For future filtering logic
```
### Run Docker Compose
`docker compose up --build -d`

### Edit your Mosquitto broker
-> Set `allow_anonymous` to `true` which is default setup for a broker, this set the broker open for everyone  
-> Or keep it false and uncomment the last 2 lines to enable authentication
```
password_file /mosquitto/config/passwd #Read passwd file
acl_file /mosquitto/config/mosquitto.acl #Read ACL file
```
There is a script that will create `passwd` and `mosquitto.acl` files
`passwd` stores your authentication setup (username and password), and only allowing that specific user to publish and subscribe to a broker
```
username = <password_hash>
```
Access Control List, `mosquitto.acl` file allows your to restrict access to topics so that only authorized users/clients can publish or subscribe to them.
```
user <username>  
topic readwrite <mqtt topic>
```
The script will then generate a default testuser and allow this specific user to publish message to MQTT Broker
```
testclient
testpassword
```
You can edit the script file to use your own username and password  

Try to communicate with the broker with/without username and password  
see the different  
`mosquitto_sub -h localhost -t <topic>`  
This will return  
`Connection error: Connection Refused: not authorised.`    

Now try  
`mosquitto_sub -h localhost -t <topic> -u <username> -P <password>`

## Access INFLUXDB
You can access InfluxDB via the web interface, which is available at `http://localhost:8086`
# Setup Weather Edge
Clone this repo to your Raspberry Pi (Debian, Ubuntu are ok)  
```
git clone https://github.com/Itea-Lab/Weather-Edge.git
```  

```
cd Weather-Edge
```

### Create an .env file to store necessary credentials 
`sudo nano .env`
```
INFLUXDB_USERNAME=<INFLUXDB USERNAME>

INFLUXDB_PASSWORD=<INFLUXDB-PASSWORD>

INFLUXDB_ORG=<ORGANIZATION NAME>

INFLUXDB_BUCKET=<BUCKETNAME>
```
### Run Docker Compose
`docker compose up --build -d`
### Edit your Mosquitto broker
`cd mosquitto-config `
There you will see `mosquitto.conf` file which setup the mqtt broker, the current configuration only allow specific connection to the broker, you can either

->Set `allow_anonymous` to `true` which is default setup for a broker, this set the broker open for everyone

->Or keep it false and uncomment the last 2 lines to enable authentication
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
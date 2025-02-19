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
There you will see `mosquitto.conf` file which setup the mqtt broker, the current configuration down allow any connection to the broker, you can either

->Set `allow_anonymous` to `true` which is default setup for a broker

->Or uncomment the last 2 lines to enable authentication
```
password_file /mosquitto/config/passwd #Read passwd file

acl_file /mosquitto/config/mosquitto.acl #Read ACL file
```
Close the configuration file and create `passwd` and `mosquitto.acl` 
`passwd` stores your authentication setup (username and password), and only allowing that specific user to publish and subscribe to a broker

To add username and password run:  

`mosquitto_passwd -c passwd <username>`  
`-c` means to create new username  
`-d` means to overwrite the current file with new password  
Once finish, the passwd will look like this  
`<username>=<hash password>`

Access Control List, `mosquitto.acl` file allows your to restrict access to topics so that only authorized users/clients can publish or subscribe to them.
```
user <username>  
topic readwrite <mqtt topic>
```

Restart your MQTT broker after all the configurations
`docker restart mqtt-broker`  

Then try to communicate with the broker with/without username and password
see the different
`mosquitto_sub -h localhost -t <topic>`  
This will return 
`Connection error: Connection Refused: not authorised.`  

Now try  
`mosquitto_sub -h localhost -t <topic> -u <username> -P <password>`

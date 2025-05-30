import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

load_dotenv()

def connect_influxdb():
    token = os.environ.get("INFLUXDB_TOKEN")
    url = "http://localhost:8086"
    org = os.environ.get("INFLUXDB_ORG")
    
    if not token:
        raise ValueError("INFLUXDB_TOKEN environment variable is not set")
    if not org:
        raise ValueError("INFLUXDB_ORG environment variable is not set")
    try:
        client = InfluxDBClient(url=url, token=token, org=org)
        # Test connection
        client.ping()
        print("Connected to InfluxDB")
        return client
    except Exception as e:
        print(f"Failed to connect to InfluxDB: {e}")
        return None
    
def get_write_api(client):
    if client:
        return client.write_api(write_options=SYNCHRONOUS)
    return None 
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

load_dotenv()

def connect_influxdb(url, token, org):
    if not token:
        raise ValueError("InfluxDB token is required")
    if not org:
        raise ValueError("InfluxDB organization is required")
    if not url:
        raise ValueError("InfluxDB URL is required")
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
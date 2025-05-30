import os
import time
from influxdb_client import Point, WritePrecision
from .influxClient import get_write_api
from dotenv import load_dotenv

load_dotenv()

def write_data(client, bucket, measurement, data):
    org = os.environ.get("INFLUXDB_ORG")
    write_api = get_write_api(client)
    location = os.environ.get("DATA_LOCATION", "unknown")
    
    if not write_api:
        print("Failed to get write API")
        return False
    
    try:
        point = (
            Point(measurement)
            .tag("location", location)
            .field("temperature", float(data.get("Temperature", 0)))
            .field("humidity", float(data.get("Humidity", 0)))
            .field("pressure", float(data.get("Barometric Pressure", 0)))
            .field("wind_direction", int(data.get("Wind Direction", 0)))
            .field("avg_wind_speed", float(data.get("Avg Wind Speed", 0)))
            .field("max_wind_speed", float(data.get("Max Wind Speed", 0)))
            .field("rainfall_1hr", float(data.get("Rainfall (1hr)", 0)))
            .field("rainfall_24hr", float(data.get("Rainfall (24hr)", 0)))
            .time(time.time_ns(), WritePrecision.NS)
        )
        write_api.write(bucket=bucket, org=org, record=point)
        print(f"Data written to bucket: {bucket}")
        print
        return True
    except Exception as e:
        print(f"Failed to write data: {e}")
        return False
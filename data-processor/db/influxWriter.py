import time
from influxdb_client import Point, WritePrecision
from .influxClient import get_write_api

def write_data(client, bucket, measurement, data, location=None):
    write_api = get_write_api(client)
    
    if not location:
        from config import Config
        location = Config.DATA_LOCATION
    
    if not write_api:
        print("❌ Failed to get write API")
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
        
        write_api.write(bucket=bucket, record=point)
        print(f"✅ Data written to InfluxDB: {measurement}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to write data to InfluxDB: {e}")
        return False
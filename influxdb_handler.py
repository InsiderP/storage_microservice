import os
from datetime import datetime
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from typing import Dict, Any, List

load_dotenv()

class InfluxDBHandler:
    def __init__(self):
        self.client = InfluxDBClient(
            url=os.getenv("INFLUXDB_URL"),
            token=os.getenv("INFLUXDB_TOKEN"),
            org=os.getenv("INFLUXDB_ORG")
        )
        self.bucket = os.getenv("INFLUXDB_BUCKET")
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def store_sensor_data(self, data: Dict[str, Any]) -> bool:
        """Store sensor data in InfluxDB"""
        try:
            # Create a point with the sensor data
            point = Point("sensor_data") \
                .tag("device_id", data["device_id"]) \
                .tag("device_type", data["device_type"]) \
                .time(data["timestamp"])
            
            # Add all fields from the sensor data
            for key, value in data.items():
                if key not in ["device_id", "device_type", "timestamp"]:
                    point.field(key, value)
            
            # Write the point to InfluxDB
            self.client.write_api(write_options=SYNCHRONOUS).write(
                bucket=self.bucket,
                org=self.org,
                record=point
            )
            return True
        except Exception as e:
            print(f"Error storing sensor data: {str(e)}")
            return False

    def query_sensor_data(self, device_id: str, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """Query sensor data from InfluxDB"""
        try:
            # Build the Flux query
            query = f'''
                from(bucket: "{self.bucket}")
                    |> range(start: {start_time}, stop: {end_time})
                    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
                    |> filter(fn: (r) => r["device_id"] == "{device_id}")
                    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
            
            # Execute the query
            result = self.client.query_api().query(query=query, org=self.org)
            
            # Process the results
            data = []
            for table in result:
                for record in table.records:
                    record_data = {
                        "timestamp": record.get_time().isoformat(),
                        "device_id": record.values.get("device_id"),
                        "device_type": record.values.get("device_type")
                    }
                    # Add all fields from the record
                    for key, value in record.values.items():
                        if key not in ["_start", "_stop", "_time", "device_id", "device_type"]:
                            record_data[key] = value
                    data.append(record_data)
            return data
        except Exception as e:
            print(f"Error querying sensor data: {str(e)}")
            return []

    def query_device_types(self) -> List[str]:
        """Query all unique device types"""
        try:
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -30d)
                |> filter(fn: (r) => r["_measurement"] == "sensor_data")
                |> distinct(column: "device_type")
            '''
            
            result = self.client.query_api().query(query)
            device_types = []
            
            for table in result:
                for record in table.records:
                    device_types.append(record.values.get("device_type"))
            
            return list(set(device_types))
        except Exception as e:
            print(f"Error querying device types: {str(e)}")
            return []

    def query_device_locations(self) -> List[str]:
        """Query all unique device locations"""
        try:
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -30d)
                |> filter(fn: (r) => r["_measurement"] == "sensor_data")
                |> distinct(column: "location")
            '''
            
            result = self.client.query_api().query(query)
            locations = []
            
            for table in result:
                for record in table.records:
                    locations.append(record.values.get("location"))
            
            return list(set(locations))
        except Exception as e:
            print(f"Error querying device locations: {str(e)}")
            return []

    def close(self):
        """Close the InfluxDB client connection"""
        self.client.close() 
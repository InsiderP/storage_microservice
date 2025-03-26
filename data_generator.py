from datetime import datetime, timedelta
import random
import json
from typing import Dict, Any, List

class IoTDataGenerator:
    def __init__(self):
        self.device_types = ['thermostat', 'camera', 'motion_sensor', 'door_lock', 'smart_plug']
        self.locations = ['Living Room', 'Kitchen', 'Bedroom', 'Bathroom', 'Office']
        self.device_statuses = ['active', 'inactive', 'maintenance', 'error']

    def generate_device_data(self, num_devices: int = 5) -> List[Dict[str, Any]]:
        """Generate dummy IoT device data"""
        devices = []
        for i in range(num_devices):
            device_id = f"device_{i+1}"
            device_type = random.choice(self.device_types)
            location = random.choice(self.locations)
            status = random.choice(self.device_statuses)
            
            # Generate sensor readings based on device type
            sensor_data = self._generate_sensor_readings(device_type)
            
            device = {
                "device_id": device_id,
                "device_type": device_type,
                "location": location,
                "status": status,
                "sensor_data": sensor_data,
                "timestamp": datetime.utcnow().isoformat(),
                "image_url": f"s3://smart-home-data/images/{device_id}.jpg"
            }
            devices.append(device)
        
        return devices

    def _generate_sensor_readings(self, device_type: str) -> Dict[str, Any]:
        """Generate sensor readings based on device type"""
        timestamp = datetime.utcnow().isoformat()
        
        if device_type == 'thermostat':
            return {
                "temperature": round(random.uniform(18, 25), 1),
                "humidity": round(random.uniform(40, 60), 1),
                "pressure": round(random.uniform(1000, 1020), 1),
                "timestamp": timestamp
            }
        elif device_type == 'camera':
            return {
                "motion_detected": random.choice([True, False]),
                "brightness": round(random.uniform(0, 100), 1),
                "timestamp": timestamp
            }
        elif device_type == 'motion_sensor':
            return {
                "motion_detected": random.choice([True, False]),
                "sensitivity": round(random.uniform(0.5, 1.0), 2),
                "timestamp": timestamp
            }
        elif device_type == 'door_lock':
            return {
                "locked": random.choice([True, False]),
                "battery_level": round(random.uniform(80, 100), 1),
                "timestamp": timestamp
            }
        elif device_type == 'smart_plug':
            return {
                "power_on": random.choice([True, False]),
                "energy_usage": round(random.uniform(0, 100), 1),
                "timestamp": timestamp
            }
        else:
            raise ValueError(f"Unknown device type: {device_type}")

    def generate_time_series_data(self, device_id: str, device_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Generate time series data for a device"""
        data = []
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        current_time = start_time
        while current_time <= end_time:
            sensor_data = self._generate_sensor_readings(device_type)
            sensor_data["timestamp"] = current_time.isoformat()
            data.append(sensor_data)
            current_time += timedelta(minutes=5)  # Data every 5 minutes
        
        return data

    def generate_device_metadata(self, device_id: str) -> Dict[str, Any]:
        """Generate device metadata"""
        return {
            "device_id": device_id,
            "device_type": random.choice(self.device_types),
            "location": random.choice(self.locations),
            "manufacturer": random.choice(["SmartHome Inc", "IoT Solutions", "HomeTech"]),
            "firmware_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
            "last_maintenance": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(30, 365))).isoformat()
        }

    def generate_system_logs(self, device_id: str, num_logs: int = 10) -> List[Dict[str, Any]]:
        """Generate system logs for a device"""
        log_types = ['status_change', 'maintenance', 'error', 'update']
        logs = []
        
        for i in range(num_logs):
            log = {
                "log_id": f"log_{i+1}",
                "device_id": device_id,
                "event_type": random.choice(log_types),
                "message": f"Device {device_id} {random.choice(log_types)} event",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat()
            }
            logs.append(log)
        
        return logs

    def generate_complete_dataset(self, num_devices: int = 5) -> Dict[str, Any]:
        """Generate complete dataset for all devices"""
        devices = self.generate_device_data(num_devices)
        complete_data = {
            "devices": devices,
            "metadata": {},
            "logs": {}
        }
        
        for device in devices:
            device_id = device["device_id"]
            complete_data["metadata"][device_id] = self.generate_device_metadata(device_id)
            complete_data["logs"][device_id] = self.generate_system_logs(device_id)
        
        return complete_data 
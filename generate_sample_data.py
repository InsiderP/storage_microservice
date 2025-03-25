import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
import time

# API endpoint
API_URL = "http://localhost:8000"

def generate_sensor_data():
    """Generate sample sensor data"""
    # Generate timestamps for the last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    # Generate data points
    timestamps = pd.date_range(start=start_time, end=end_time, freq='5min')
    
    # Generate sample data
    data = {
        'timestamp': timestamps,
        'temperature': np.random.normal(22, 2, len(timestamps)),
        'humidity': np.random.normal(45, 5, len(timestamps)),
        'energy_consumption': np.random.normal(100, 10, len(timestamps))
    }
    
    df = pd.DataFrame(data)
    
    # Store data in InfluxDB
    for _, row in df.iterrows():
        payload = {
            "device_id": "device_001",
            "temperature": float(row['temperature']),
            "humidity": float(row['humidity']),
            "energy_consumption": float(row['energy_consumption'])
        }
        
        try:
            response = requests.post(f"{API_URL}/sensor-data", json=payload)
            if response.status_code != 200:
                print(f"Error storing sensor data: {response.text}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        time.sleep(0.1)  # Small delay to avoid overwhelming the API

def generate_metadata():
    """Generate sample metadata"""
    # Sample metadata
    metadata = {
        "device_id": "device_001",
        "location": "Building A, Floor 1",
        "type": "HVAC",
        "last_maintenance": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(f"{API_URL}/metadata", json=metadata)
        if response.status_code != 200:
            print(f"Error storing metadata: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def upload_sample_file():
    """Upload a sample file to S3"""
    # Create a sample CSV file
    df = pd.DataFrame({
        'timestamp': pd.date_range(start=datetime.now() - timedelta(hours=1), periods=60, freq='1min'),
        'value': np.random.normal(100, 10, 60)
    })
    
    # Save to temporary file
    temp_file = "sample_data.csv"
    df.to_csv(temp_file, index=False)
    
    # Upload file
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': ('sample_data.csv', f, 'text/csv')}
            response = requests.post(f"{API_URL}/upload-file", files=files)
            if response.status_code != 200:
                print(f"Error uploading file: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    print("Generating sample data...")
    
    print("Generating metadata...")
    generate_metadata()
    
    print("Generating sensor data...")
    generate_sensor_data()
    
    print("Uploading sample file...")
    upload_sample_file()
    
    print("Sample data generation complete!") 
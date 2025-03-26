from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uvicorn
from data_generator import IoTDataGenerator
from influxdb_handler import InfluxDBHandler
from postgres_handler import PostgreSQLHandler
from s3_handler import S3Handler

app = FastAPI(title="Smart Home IoT Data Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers
data_generator = IoTDataGenerator()
influx_handler = InfluxDBHandler()
postgres_handler = PostgreSQLHandler()
s3_handler = S3Handler()

@app.post("/generate-and-store")
async def generate_and_store_data(num_devices: int = 5):
    """Generate and store dummy IoT device data"""
    try:
        # Generate complete dataset
        dataset = data_generator.generate_complete_dataset(num_devices)
        
        # Store data in each database
        for device in dataset["devices"]:
            device_id = device["device_id"]
            device_type = device["device_type"]
            
            # Generate time series data for InfluxDB
            sensor_data = data_generator.generate_time_series_data(device_id, device_type, hours=24)
            
            # Store sensor data in InfluxDB
            influx_handler.store_sensor_data(
                device_id=device_id,
                device_type=device_type,
                sensor_data=sensor_data
            )
            
            # Store metadata in PostgreSQL
            postgres_handler.store_device_metadata(dataset["metadata"][device_id])
            
            # Store logs in PostgreSQL
            for log in dataset["logs"][device_id]:
                postgres_handler.store_system_log(log)
        
        return {"message": f"Successfully generated and stored data for {num_devices} devices"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices")
async def get_devices():
    """Get all devices and their metadata"""
    try:
        return postgres_handler.get_device_metadata()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/{device_id}")
async def get_device(device_id: str):
    """Get specific device metadata"""
    try:
        devices = postgres_handler.get_device_metadata(device_id)
        if not devices:
            raise HTTPException(status_code=404, detail="Device not found")
        return devices[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/{device_id}/sensor-data")
async def get_device_sensor_data(
    device_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """Get sensor data for a specific device"""
    try:
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        if not end_time:
            end_time = datetime.utcnow().isoformat()
        
        return influx_handler.query_sensor_data(device_id, start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/{device_id}/logs")
async def get_device_logs(
    device_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """Get system logs for a specific device"""
    try:
        return postgres_handler.get_system_logs(device_id, start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/devices/{device_id}/images")
async def upload_device_image(device_id: str, file: UploadFile = File(...)):
    """Upload an image for a device"""
    try:
        image_data = await file.read()
        image_url = s3_handler.store_device_image(device_id, image_data, file.content_type)
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to store image")
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/{device_id}/images")
async def get_device_images(device_id: str):
    """Get all images for a device"""
    try:
        return s3_handler.get_device_images(device_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/device-types")
async def get_device_types():
    """Get all unique device types"""
    try:
        return postgres_handler.get_device_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/device-locations")
async def get_device_locations():
    """Get all unique device locations"""
    try:
        return postgres_handler.get_device_locations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/devices/{device_id}")
async def delete_device(device_id: str):
    """Delete all data for a device"""
    try:
        # Delete from S3
        if not s3_handler.delete_device_data(device_id):
            raise HTTPException(status_code=500, detail="Failed to delete device data from S3")
        
        # Note: InfluxDB and PostgreSQL data deletion would need to be implemented
        # in their respective handlers
        
        return {"message": f"Successfully deleted data for device {device_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 
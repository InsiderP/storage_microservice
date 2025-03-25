from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import psycopg2
from psycopg2.extras import RealDictCursor
import boto3
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import json
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

app = FastAPI(title="Smart Building Data Storage Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# InfluxDB client
influx_client = influxdb_client.InfluxDBClient(
    url=os.getenv("INFLUXDB_URL"),
    token=os.getenv("INFLUXDB_TOKEN"),
    org=os.getenv("INFLUXDB_ORG")
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# PostgreSQL connection
def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

# S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

@app.post("/sensor-data")
async def store_sensor_data(data: Dict[str, Any]):
    """Store sensor data in InfluxDB"""
    try:
        point = influxdb_client.Point("sensor_measurement")\
            .tag("device_id", data.get("device_id"))\
            .field("temperature", data.get("temperature"))\
            .field("humidity", data.get("humidity"))\
            .field("energy_consumption", data.get("energy_consumption"))\
            .time(datetime.utcnow())
        
        write_api.write(bucket=os.getenv("INFLUXDB_BUCKET"), record=point)
        return {"message": "Sensor data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/metadata")
async def store_metadata(data: Dict[str, Any]):
    """Store metadata in PostgreSQL"""
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO metadata (device_id, location, type, last_maintenance)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (device_id) DO UPDATE
            SET location = EXCLUDED.location,
                type = EXCLUDED.type,
                last_maintenance = EXCLUDED.last_maintenance
        """, (
            data.get("device_id"),
            data.get("location"),
            data.get("type"),
            data.get("last_maintenance")
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Metadata stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload file to S3"""
    try:
        file_content = await file.read()
        s3_client.put_object(
            Bucket=os.getenv("S3_BUCKET_NAME"),
            Key=f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}",
            Body=file_content
        )
        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sensor-data/{device_id}")
async def get_sensor_data(device_id: str, start_time: str, end_time: str):
    """Retrieve sensor data from InfluxDB"""
    try:
        query = f'''
        from(bucket: "{os.getenv("INFLUXDB_BUCKET")}")
            |> range(start: {start_time}, stop: {end_time})
            |> filter(fn: (r) => r["device_id"] == "{device_id}")
        '''
        result = influx_client.query_api().query(query)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metadata/{device_id}")
async def get_metadata(device_id: str):
    """Retrieve metadata from PostgreSQL"""
    try:
        conn = get_postgres_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT * FROM metadata WHERE device_id = %s
        """, (device_id,))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Device not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files():
    """List files in S3 bucket"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=os.getenv("S3_BUCKET_NAME")
        )
        files = [{"key": obj["Key"], "size": obj["Size"]} for obj in response.get("Contents", [])]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("API_HOST"), port=int(os.getenv("API_PORT"))) 
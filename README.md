# Smart Home IoT Data Service

This microservice handles data storage and retrieval for smart home IoT devices, utilizing a multi-database architecture:

- **InfluxDB**: Time-series data storage for sensor readings
- **PostgreSQL**: Relational data storage for device metadata and system logs
- **AWS S3**: Object storage for device images and log files

## Architecture Overview

```
         ┌──────────────┐
         │ Smart Home    │
         │ IoT Devices   │
         └──────┬────────┘
                │
                ▼
      ┌────────────────────┐
      │   Data Ingestion    │
      │  (Dummy Data Gen.)  │
      └────────┬────────────┘
                │
                ▼
      ┌────────────────────┐
      │  FastAPI Service   │
      │   (Port 8001)      │
      └───────┬────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
InfluxDB   PostgreSQL   AWS S3
(Time-Series) (Metadata) (Files/Logs)
```

## Prerequisites

- Python 3.8+
- InfluxDB Cloud account
- PostgreSQL database
- AWS account with S3 access

## Configuration

Create a `.env` file in the project root with the following variables:

```env
INFLUXDB_URL=your_influxdb_url
INFLUXDB_TOKEN=your_influxdb_token
INFLUXDB_ORG=your_org
INFLUXDB_BUCKET=your_bucket

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=smart_building
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
S3_BUCKET_NAME=your_bucket_name
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the FastAPI service:
```bash
python main.py
```

2. The service will be available at `http://localhost:8001`

3. API Documentation will be available at:
   - Swagger UI: `http://localhost:8001/docs`
   - ReDoc: `http://localhost:8001/redoc`

## API Endpoints

### Data Generation
- `POST /generate-and-store`: Generate and store dummy IoT device data
  - Query parameter: `num_devices` (default: 5)

### Device Management
- `GET /devices`: Get all devices and their metadata
- `GET /devices/{device_id}`: Get specific device metadata
- `DELETE /devices/{device_id}`: Delete all data for a device

### Sensor Data
- `GET /devices/{device_id}/sensor-data`: Get sensor data for a device
  - Query parameters: `start_time`, `end_time` (optional)

### System Logs
- `GET /devices/{device_id}/logs`: Get system logs for a device
  - Query parameters: `start_time`, `end_time` (optional)

### Device Images
- `POST /devices/{device_id}/images`: Upload an image for a device
- `GET /devices/{device_id}/images`: Get all images for a device

### Device Information
- `GET /device-types`: Get all unique device types
- `GET /device-locations`: Get all unique device locations

## Data Structure

### Device Types
- Thermostat
- Camera
- Motion Sensor
- Door Lock
- Smart Plug

### Sensor Data (by device type)
- Thermostat: temperature, humidity, pressure
- Camera: motion_detected, brightness
- Motion Sensor: motion_detected, sensitivity
- Door Lock: locked, battery_level
- Smart Plug: power_on, energy_usage

## Example Usage

1. Generate and store dummy data:
```bash
curl -X POST "http://localhost:8001/generate-and-store?num_devices=5"
```

2. Get all devices:
```bash
curl "http://localhost:8001/devices"
```

3. Get sensor data for a device:
```bash
curl "http://localhost:8001/devices/device_1/sensor-data"
```

4. Upload a device image:
```bash
curl -X POST -F "file=@image.jpg" "http://localhost:8001/devices/device_1/images"
```

## Error Handling

The service includes comprehensive error handling for:
- Database connection issues
- Invalid device IDs
- File upload failures
- Data validation errors

All errors are returned with appropriate HTTP status codes and error messages. 
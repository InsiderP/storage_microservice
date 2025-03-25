# Smart Building Data Storage Service

This microservice handles data storage for a smart building system, managing sensor data, metadata, and file storage using InfluxDB, PostgreSQL, and AWS S3.

## Features

- Time-series data storage using InfluxDB
- Relational data storage using PostgreSQL
- File storage using AWS S3
- RESTful API endpoints for data operations
- Sample data generation for testing

## Prerequisites

- Docker and Docker Compose
- AWS S3 bucket and credentials
- Python 3.11 or higher (for local development)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration

3. Start the services using Docker Compose:
```bash
docker-compose up -d
```

4. Generate sample data (optional):
```bash
python generate_sample_data.py
```

## API Endpoints

### Sensor Data

- `POST /sensor-data`: Store sensor data in InfluxDB
- `GET /sensor-data/{device_id}`: Retrieve sensor data for a specific device

### Metadata

- `POST /metadata`: Store device metadata in PostgreSQL
- `GET /metadata/{device_id}`: Retrieve metadata for a specific device

### File Storage

- `POST /upload-file`: Upload a file to S3
- `GET /files`: List files in the S3 bucket

## Example Usage

### Store Sensor Data
```bash
curl -X POST http://localhost:8000/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device_001",
    "temperature": 22.5,
    "humidity": 45.0,
    "energy_consumption": 100.0
  }'
```

### Store Metadata
```bash
curl -X POST http://localhost:8000/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device_001",
    "location": "Building A, Floor 1",
    "type": "HVAC",
    "last_maintenance": "2024-02-20T10:00:00Z"
  }'
```

### Upload File
```bash
curl -X POST http://localhost:8000/upload-file \
  -F "file=@/path/to/your/file.csv"
```

## Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service locally:
```bash
uvicorn main:app --reload
```

3. Access the API documentation:
   - Open http://localhost:8000/docs in your browser
   - Explore the available endpoints and their documentation

## Testing

The service includes a sample data generation script that can be used for testing:

```bash
python generate_sample_data.py
```

This script will:
1. Generate sample metadata
2. Generate 24 hours of sensor data
3. Upload a sample CSV file

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
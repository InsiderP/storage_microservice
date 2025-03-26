import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

class PostgreSQLHandler:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        # Drop old tables if they exist
        self.cur.execute("""
            DROP TABLE IF EXISTS system_logs CASCADE;
            DROP TABLE IF EXISTS device_metadata CASCADE;
        """)

        # Create device metadata table
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS device_metadata (
                device_id VARCHAR(50) PRIMARY KEY,
                device_type VARCHAR(50),
                location VARCHAR(100),
                manufacturer VARCHAR(100),
                firmware_version VARCHAR(20),
                last_maintenance TIMESTAMP,
                created_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create system logs table
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                log_id SERIAL PRIMARY KEY,
                device_id VARCHAR(50) REFERENCES device_metadata(device_id),
                event_type VARCHAR(50),
                message TEXT,
                timestamp TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def store_device_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Store device metadata in PostgreSQL"""
        try:
            self.cur.execute("""
                INSERT INTO device_metadata (
                    device_id, device_type, location, manufacturer,
                    firmware_version, last_maintenance, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (device_id) DO UPDATE SET
                    device_type = EXCLUDED.device_type,
                    location = EXCLUDED.location,
                    manufacturer = EXCLUDED.manufacturer,
                    firmware_version = EXCLUDED.firmware_version,
                    last_maintenance = EXCLUDED.last_maintenance,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                metadata["device_id"],
                metadata["device_type"],
                metadata["location"],
                metadata["manufacturer"],
                metadata["firmware_version"],
                metadata["last_maintenance"],
                metadata["created_at"]
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error storing device metadata: {str(e)}")
            self.conn.rollback()
            return False

    def store_system_log(self, log: Dict[str, Any]) -> bool:
        """Store system log in PostgreSQL"""
        try:
            self.cur.execute("""
                INSERT INTO system_logs (
                    device_id, event_type, message, timestamp
                ) VALUES (%s, %s, %s, %s)
            """, (
                log["device_id"],
                log["event_type"],
                log["message"],
                log["timestamp"]
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error storing system log: {str(e)}")
            self.conn.rollback()
            return False

    def get_device_metadata(self, device_id: str = None) -> List[Dict[str, Any]]:
        """Get device metadata for a specific device or all devices"""
        try:
            if device_id:
                self.cur.execute("""
                    SELECT * FROM device_metadata WHERE device_id = %s
                """, (device_id,))
            else:
                self.cur.execute("SELECT * FROM device_metadata")
            return self.cur.fetchall()
        except Exception as e:
            print(f"Error querying device metadata: {str(e)}")
            return []

    def get_system_logs(self, device_id: str = None, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """Get system logs with optional filters"""
        try:
            query = "SELECT * FROM system_logs WHERE 1=1"
            params = []

            if device_id:
                query += " AND device_id = %s"
                params.append(device_id)
            if start_time:
                query += " AND timestamp >= %s"
                params.append(start_time)
            if end_time:
                query += " AND timestamp <= %s"
                params.append(end_time)

            query += " ORDER BY timestamp DESC"

            self.cur.execute(query, params)
            return self.cur.fetchall()
        except Exception as e:
            print(f"Error querying system logs: {str(e)}")
            return []

    def get_device_types(self) -> List[str]:
        """Get all unique device types"""
        try:
            self.cur.execute("SELECT DISTINCT device_type FROM device_metadata")
            return [row["device_type"] for row in self.cur.fetchall()]
        except Exception as e:
            print(f"Error querying device types: {str(e)}")
            return []

    def get_device_locations(self) -> List[str]:
        """Get all unique device locations"""
        try:
            self.cur.execute("SELECT DISTINCT location FROM device_metadata")
            return [row["location"] for row in self.cur.fetchall()]
        except Exception as e:
            print(f"Error querying device locations: {str(e)}")
            return []

    def close(self):
        """Close the PostgreSQL connection"""
        self.cur.close()
        self.conn.close() 
import os
import boto3
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, List
import json

load_dotenv()

class S3Handler:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    def store_device_image(self, device_id: str, image_data: bytes, content_type: str = 'image/jpeg') -> str:
        """Store device image in S3"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            key = f"images/{device_id}/{timestamp}.jpg"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_data,
                ContentType=content_type
            )
            
            return f"s3://{self.bucket_name}/{key}"
        except Exception as e:
            print(f"Error storing device image: {str(e)}")
            return None

    def store_device_log(self, device_id: str, log_data: Dict[str, Any]) -> str:
        """Store device log in S3"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            key = f"logs/{device_id}/{timestamp}.json"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(log_data),
                ContentType='application/json'
            )
            
            return f"s3://{self.bucket_name}/{key}"
        except Exception as e:
            print(f"Error storing device log: {str(e)}")
            return None

    def get_device_images(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all images for a device"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"images/{device_id}/"
            )
            
            images = []
            for obj in response.get('Contents', []):
                images.append({
                    'key': obj['Key'],
                    'url': f"s3://{self.bucket_name}/{obj['Key']}",
                    'timestamp': obj['LastModified'].isoformat(),
                    'size': obj['Size']
                })
            
            return sorted(images, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            print(f"Error getting device images: {str(e)}")
            return []

    def get_device_logs(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a device"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"logs/{device_id}/"
            )
            
            logs = []
            for obj in response.get('Contents', []):
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
                log_data = json.loads(response['Body'].read().decode('utf-8'))
                
                logs.append({
                    'key': obj['Key'],
                    'url': f"s3://{self.bucket_name}/{obj['Key']}",
                    'timestamp': obj['LastModified'].isoformat(),
                    'data': log_data
                })
            
            return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            print(f"Error getting device logs: {str(e)}")
            return []

    def delete_device_data(self, device_id: str) -> bool:
        """Delete all data for a device"""
        try:
            # Delete images
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"images/{device_id}/"
            )
            for obj in response.get('Contents', []):
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
            
            # Delete logs
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"logs/{device_id}/"
            )
            for obj in response.get('Contents', []):
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
            
            return True
        except Exception as e:
            print(f"Error deleting device data: {str(e)}")
            return False

    def store_device_document(self, device_id: str, document_data: bytes, document_type: str):
        """Store device document in S3"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        key = f"devices/{device_id}/documents/{timestamp}.{document_type}"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=document_data,
                ContentType=f'application/{document_type}'
            )
            print(f"Successfully stored document for device {device_id}")
            return key
        except Exception as e:
            print(f"Error storing document in S3: {str(e)}")
            raise

    def get_device_image(self, device_id: str, image_key: str):
        """Retrieve device image from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=image_key
            )
            return response['Body'].read()
        except Exception as e:
            print(f"Error retrieving image from S3: {str(e)}")
            raise

    def get_device_document(self, device_id: str, document_key: str):
        """Retrieve device document from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=document_key
            )
            return response['Body'].read()
        except Exception as e:
            print(f"Error retrieving document from S3: {str(e)}")
            raise

    def list_device_files(self, device_id: str, file_type: str = None):
        """List all files for a device in S3"""
        prefix = f"devices/{device_id}/"
        if file_type:
            prefix += f"{file_type}s/"
            
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            print(f"Error listing files in S3: {str(e)}")
            raise 
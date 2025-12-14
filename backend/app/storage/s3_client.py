import boto3
from botocore.exceptions import ClientError
from app.config import settings
from typing import BinaryIO, Optional
import uuid


class S3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.s3_bucket_name
    
    def upload_file(self, file_content: BinaryIO, s3_key: str, content_type: Optional[str] = None) -> str:
        """Upload a file to S3 and return the S3 key"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.upload_fileobj(
                file_content,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            return s3_key
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def download_file(self, s3_key: str) -> bytes:
        """Download a file from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Failed to download file from S3: {str(e)}")
    
    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for temporary access"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def generate_key(self, sme_id: int, document_type: str, filename: str) -> str:
        """Generate a unique S3 key for a document"""
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        unique_id = str(uuid.uuid4())
        return f"smes/{sme_id}/{document_type}/{unique_id}.{file_extension}"


s3_client = S3Client()

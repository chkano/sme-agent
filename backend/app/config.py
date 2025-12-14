from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database (Supabase)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    database_url: Optional[str] = None
    
    # AWS S3
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: Optional[str] = None
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # JWT
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Allow missing env vars for development/docs
        extra = "ignore"


settings = Settings()

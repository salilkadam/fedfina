"""
Configuration management for the Postprocess API.

This module handles all configuration settings using Pydantic settings
for type safety and validation.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application Settings
    app_name: str = Field(default="Postprocess API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # ElevenLabs Configuration
    elevenlabs_api_key: str = Field(..., env="ELEVENLABS_API_KEY")
    elevenlabs_base_url: str = Field(
        default="https://api.elevenlabs.io/v1", 
        env="ELEVENLABS_BASE_URL"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=5000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # MinIO Configuration
    minio_endpoint: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    minio_bucket_name: str = Field(default="fedfina-reports", env="MINIO_BUCKET_NAME")
    minio_secure: bool = Field(default=False, env="MINIO_SECURE")
    minio_region: str = Field(default="us-east-1", env="MINIO_REGION")
    
    # Email Configuration
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(..., env="SMTP_USERNAME")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    smtp_from_email: str = Field(..., env="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="Postprocess API", env="SMTP_FROM_NAME")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    smtp_use_cc: Optional[str] = Field(default=None, env="SMTP_USE_CC")
    
    # API Security
    api_secret_key: str = Field(..., env="API_SECRET_KEY")
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    rate_limit_per_minute: int = Field(default=10, env="RATE_LIMIT_PER_MINUTE")
    
    # Download Token Configuration
    download_token_expiry_hours: int = Field(default=24, env="DOWNLOAD_TOKEN_EXPIRY_HOURS")
    
    # Callback Configuration
    callback_enabled: bool = Field(default=True, env="CALLBACK_ENABLED")
    callback_url: str = Field(
        default="https://hr.fedfina.com/salespd/api/saveVoicePD",
        env="CALLBACK_URL"
    )
    callback_timeout_seconds: int = Field(default=30, env="CALLBACK_TIMEOUT_SECONDS")
    
    # Processing Settings
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    processing_timeout_minutes: int = Field(default=10, env="PROCESSING_TIMEOUT_MINUTES")
    enable_audio_storage: bool = Field(default=True, env="ENABLE_AUDIO_STORAGE")
    enable_transcript_storage: bool = Field(default=True, env="ENABLE_TRANSCRIPT_STORAGE")
    enable_report_generation: bool = Field(default=True, env="ENABLE_REPORT_GENERATION")
    
    # File Retention
    file_retention_days: int = Field(default=30, env="FILE_RETENTION_DAYS")
    audit_log_retention_days: int = Field(default=90, env="AUDIT_LOG_RETENTION_DAYS")
    
    # Logging
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()
    
    @validator('openai_temperature')
    def validate_temperature(cls, v):
        """Validate OpenAI temperature"""
        if not 0 <= v <= 2:
            raise ValueError('temperature must be between 0 and 2')
        return v
    
    @validator('max_file_size_mb')
    def validate_file_size(cls, v):
        """Validate max file size"""
        if v <= 0 or v > 100:
            raise ValueError('max_file_size_mb must be between 1 and 100')
        return v
    
    @validator('processing_timeout_minutes')
    def validate_timeout(cls, v):
        """Validate processing timeout"""
        if v <= 0 or v > 60:
            raise ValueError('processing_timeout_minutes must be between 1 and 60')
        return v
    
    @validator('download_token_expiry_hours')
    def validate_token_expiry(cls, v):
        """Validate download token expiry hours"""
        if v <= 0 or v > 168:  # Max 1 week (168 hours)
            raise ValueError('download_token_expiry_hours must be between 1 and 168')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings

"""
SQLAlchemy database models for the Postprocess API.

This module contains all the database models for tracking conversation processing,
file storage, and audit logging.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Interval, JSON, 
    Boolean, BigInteger, CheckConstraint, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()


class ConversationProcessing(Base):
    """Main table for tracking conversation processing jobs"""
    
    __tablename__ = 'conversation_processing'
    
    id = Column(Integer, primary_key=True)
    processing_id = Column(String(255), unique=True, nullable=False, index=True)
    conversation_id = Column(String(255), nullable=False, index=True)
    email_id = Column(String(255), nullable=False)
    account_id = Column(String(255), nullable=False, index=True)
    
    # Processing Status
    status = Column(String(50), default='pending', nullable=False, index=True)
    progress = Column(Integer, default=0)
    current_step = Column(String(100))
    error_message = Column(Text)
    
    # Timing Information
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)
    total_duration = Column(Interval)
    
    # File URLs
    minio_transcript_url = Column(Text)
    minio_audio_url = Column(Text)
    minio_report_url = Column(Text)
    
    # AI Processing Results
    openai_summary = Column(Text)
    summary_topic = Column(String(255))
    summary_sentiment = Column(String(50))
    summary_key_points = Column(JSON)
    summary_action_items = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    files = relationship("ConversationFiles", back_populates="processing")
    audit_logs = relationship("ProcessingAuditLog", back_populates="processing")
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'extracting', 'storing', 'summarizing', "
            "'generating_report', 'sending_email', 'completed', 'failed', 'cancelled')"
        ),
        CheckConstraint("progress >= 0 AND progress <= 100"),
        CheckConstraint("summary_sentiment IN ('positive', 'negative', 'neutral', 'mixed')"),
        Index('idx_conversation_processing_conversation_id', 'conversation_id'),
        Index('idx_conversation_processing_account_id', 'account_id'),
        Index('idx_conversation_processing_status', 'status'),
        Index('idx_conversation_processing_created_at', 'created_at'),
    )


class ConversationFiles(Base):
    """Track individual files associated with conversations"""
    
    __tablename__ = 'conversation_files'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(255), nullable=False, index=True)
    account_id = Column(String(255), nullable=False, index=True)
    file_type = Column(String(50), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger)
    minio_path = Column(Text, nullable=False)
    minio_url = Column(Text)
    url_expires_at = Column(DateTime)
    
    # File metadata
    content_type = Column(String(100))
    checksum = Column(String(64))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    processing = relationship("ConversationProcessing", back_populates="files")
    
    __table_args__ = (
        CheckConstraint("file_type IN ('transcript', 'audio', 'report', 'summary')"),
        CheckConstraint("file_size >= 0"),
        Index('idx_conversation_files_conversation_id', 'conversation_id'),
        Index('idx_conversation_files_account_id', 'account_id'),
        Index('idx_conversation_files_file_type', 'file_type'),
    )


class ProcessingAuditLog(Base):
    """Track all processing events and operations"""
    
    __tablename__ = 'processing_audit_log'
    
    id = Column(Integer, primary_key=True)
    processing_id = Column(String(255), nullable=False, index=True)
    conversation_id = Column(String(255), nullable=False, index=True)
    account_id = Column(String(255), nullable=False)
    
    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    event_status = Column(String(50), nullable=False)
    step_name = Column(String(100))
    step_duration = Column(Interval)
    
    # Event data
    event_data = Column(JSON)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Timing
    created_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    processing = relationship("ConversationProcessing", back_populates="audit_logs")
    
    __table_args__ = (
        CheckConstraint("event_status IN ('started', 'completed', 'failed', 'retried')"),
        CheckConstraint("retry_count >= 0"),
        Index('idx_processing_audit_log_processing_id', 'processing_id'),
        Index('idx_processing_audit_log_conversation_id', 'conversation_id'),
        Index('idx_processing_audit_log_event_type', 'event_type'),
        Index('idx_processing_audit_log_created_at', 'created_at'),
    )


class AccountSettings(Base):
    """Store account-specific configuration for postprocess operations"""
    
    __tablename__ = 'account_settings'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Email settings
    default_email_template = Column(Text)
    email_subject_template = Column(String(255))
    email_from_name = Column(String(255))
    email_from_address = Column(String(255))
    
    # Processing settings
    max_file_size_mb = Column(Integer, default=10)
    processing_timeout_minutes = Column(Integer, default=10)
    enable_audio_storage = Column(Boolean, default=True)
    enable_transcript_storage = Column(Boolean, default=True)
    enable_report_generation = Column(Boolean, default=True)
    
    # OpenAI settings
    openai_model = Column(String(100), default='gpt-4')
    openai_max_tokens = Column(Integer, default=1000)
    custom_system_prompt = Column(Text)
    
    # MinIO settings
    minio_bucket_name = Column(String(255))
    file_retention_days = Column(Integer, default=30)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint("max_file_size_mb > 0 AND max_file_size_mb <= 100"),
        CheckConstraint("processing_timeout_minutes > 0 AND processing_timeout_minutes <= 60"),
        CheckConstraint("file_retention_days > 0 AND file_retention_days <= 365"),
        Index('idx_account_settings_account_id', 'account_id'),
    )


class ApiUsageMetrics(Base):
    """Track API usage and rate limiting"""
    
    __tablename__ = 'api_usage_metrics'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(String(255), nullable=False, index=True)
    api_key_hash = Column(String(255), nullable=False, index=True)
    
    # Usage tracking
    endpoint = Column(String(100), nullable=False)
    request_count = Column(Integer, default=1)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Rate limiting
    rate_limit_exceeded = Column(Boolean, default=False)
    rate_limit_reset_at = Column(DateTime)
    
    # Timing
    window_start = Column(DateTime, nullable=False, index=True)
    window_end = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint("request_count >= 0 AND success_count >= 0 AND error_count >= 0"),
        Index('idx_api_usage_metrics_account_id', 'account_id'),
        Index('idx_api_usage_metrics_api_key_hash', 'api_key_hash'),
        Index('idx_api_usage_metrics_window', 'window_start', 'window_end'),
    )


# Model aliases for easier imports
ConversationProcessingModel = ConversationProcessing
ConversationFilesModel = ConversationFiles
ProcessingAuditLogModel = ProcessingAuditLog
AccountSettingsModel = AccountSettings
ApiUsageMetricsModel = ApiUsageMetrics

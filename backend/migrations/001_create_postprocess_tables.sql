-- Migration: 001_create_postprocess_tables.sql
-- Description: Create initial tables for postprocess API
-- Created: 2025-08-08

-- Create conversation_processing table
CREATE TABLE conversation_processing (
    id SERIAL PRIMARY KEY,
    processing_id VARCHAR(255) UNIQUE NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    email_id VARCHAR(255) NOT NULL,
    account_id VARCHAR(255) NOT NULL,
    
    -- Processing Status
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    current_step VARCHAR(100),
    error_message TEXT,
    
    -- Timing Information
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    estimated_completion TIMESTAMP,
    total_duration INTERVAL,
    
    -- File URLs
    minio_transcript_url TEXT,
    minio_audio_url TEXT,
    minio_report_url TEXT,
    
    -- AI Processing Results
    openai_summary TEXT,
    summary_topic VARCHAR(255),
    summary_sentiment VARCHAR(50),
    summary_key_points JSONB,
    summary_action_items JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'extracting', 'storing', 'summarizing', 'generating_report', 'sending_email', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_sentiment CHECK (summary_sentiment IN ('positive', 'negative', 'neutral', 'mixed'))
);

-- Create indexes for conversation_processing
CREATE INDEX idx_conversation_processing_conversation_id ON conversation_processing(conversation_id);
CREATE INDEX idx_conversation_processing_account_id ON conversation_processing(account_id);
CREATE INDEX idx_conversation_processing_status ON conversation_processing(status);
CREATE INDEX idx_conversation_processing_created_at ON conversation_processing(created_at);

-- Create conversation_files table
CREATE TABLE conversation_files (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    account_id VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    minio_path TEXT NOT NULL,
    minio_url TEXT,
    url_expires_at TIMESTAMP,
    
    -- File metadata
    content_type VARCHAR(100),
    checksum VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_file_type CHECK (file_type IN ('transcript', 'audio', 'report', 'summary')),
    CONSTRAINT valid_file_size CHECK (file_size >= 0)
);

-- Create indexes for conversation_files
CREATE INDEX idx_conversation_files_conversation_id ON conversation_files(conversation_id);
CREATE INDEX idx_conversation_files_account_id ON conversation_files(account_id);
CREATE INDEX idx_conversation_files_file_type ON conversation_files(file_type);

-- Create processing_audit_log table
CREATE TABLE processing_audit_log (
    id SERIAL PRIMARY KEY,
    processing_id VARCHAR(255) NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    account_id VARCHAR(255) NOT NULL,
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    event_status VARCHAR(50) NOT NULL,
    step_name VARCHAR(100),
    step_duration INTERVAL,
    
    -- Event data
    event_data JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timing
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_event_status CHECK (event_status IN ('started', 'completed', 'failed', 'retried')),
    CONSTRAINT valid_retry_count CHECK (retry_count >= 0)
);

-- Create indexes for processing_audit_log
CREATE INDEX idx_processing_audit_log_processing_id ON processing_audit_log(processing_id);
CREATE INDEX idx_processing_audit_log_conversation_id ON processing_audit_log(conversation_id);
CREATE INDEX idx_processing_audit_log_event_type ON processing_audit_log(event_type);
CREATE INDEX idx_processing_audit_log_created_at ON processing_audit_log(created_at);

-- Create account_settings table
CREATE TABLE account_settings (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Email settings
    default_email_template TEXT,
    email_subject_template VARCHAR(255),
    email_from_name VARCHAR(255),
    email_from_address VARCHAR(255),
    
    -- Processing settings
    max_file_size_mb INTEGER DEFAULT 10,
    processing_timeout_minutes INTEGER DEFAULT 10,
    enable_audio_storage BOOLEAN DEFAULT true,
    enable_transcript_storage BOOLEAN DEFAULT true,
    enable_report_generation BOOLEAN DEFAULT true,
    
    -- OpenAI settings
    openai_model VARCHAR(100) DEFAULT 'gpt-4',
    openai_max_tokens INTEGER DEFAULT 1000,
    custom_system_prompt TEXT,
    
    -- MinIO settings
    minio_bucket_name VARCHAR(255),
    file_retention_days INTEGER DEFAULT 30,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_file_size CHECK (max_file_size_mb > 0 AND max_file_size_mb <= 100),
    CONSTRAINT valid_timeout CHECK (processing_timeout_minutes > 0 AND processing_timeout_minutes <= 60),
    CONSTRAINT valid_retention CHECK (file_retention_days > 0 AND file_retention_days <= 365)
);

-- Create index for account_settings
CREATE INDEX idx_account_settings_account_id ON account_settings(account_id);

-- Create api_usage_metrics table
CREATE TABLE api_usage_metrics (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL,
    
    -- Usage tracking
    endpoint VARCHAR(100) NOT NULL,
    request_count INTEGER DEFAULT 1,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Rate limiting
    rate_limit_exceeded BOOLEAN DEFAULT false,
    rate_limit_reset_at TIMESTAMP,
    
    -- Timing
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_counts CHECK (request_count >= 0 AND success_count >= 0 AND error_count >= 0)
);

-- Create indexes for api_usage_metrics
CREATE INDEX idx_api_usage_metrics_account_id ON api_usage_metrics(account_id);
CREATE INDEX idx_api_usage_metrics_api_key_hash ON api_usage_metrics(api_key_hash);
CREATE INDEX idx_api_usage_metrics_window ON api_usage_metrics(window_start, window_end);

-- Add comments for documentation
COMMENT ON TABLE conversation_processing IS 'Main table for tracking conversation processing jobs';
COMMENT ON TABLE conversation_files IS 'Track individual files associated with conversations';
COMMENT ON TABLE processing_audit_log IS 'Track all processing events and operations';
COMMENT ON TABLE account_settings IS 'Store account-specific configuration for postprocess operations';
COMMENT ON TABLE api_usage_metrics IS 'Track API usage and rate limiting';

-- Insert default account settings for testing
INSERT INTO account_settings (account_id, email_from_name, email_from_address) 
VALUES ('test-account', 'Postprocess API', 'test@example.com')
ON CONFLICT (account_id) DO NOTHING;

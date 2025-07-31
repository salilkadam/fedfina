-- Migration: 001_create_client_interviews_table.sql
-- Description: Create the client_interviews table for storing interview details
-- Date: July 31, 2025
-- Author: AI Assistant

-- Create the client_interviews table
CREATE TABLE IF NOT EXISTS client_interviews (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) UNIQUE NOT NULL,
    officer_name VARCHAR(255) NOT NULL,
    officer_email VARCHAR(255) NOT NULL,
    client_account_id VARCHAR(255) NOT NULL,
    minio_audio_url TEXT,
    minio_transcript_url TEXT,
    minio_report_url TEXT,
    interview_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add comments to the table and columns
COMMENT ON TABLE client_interviews IS 'Stores client interview details including officer information and MinIO file URLs';
COMMENT ON COLUMN client_interviews.id IS 'Primary key for the client interview record';
COMMENT ON COLUMN client_interviews.conversation_id IS 'Unique identifier for the conversation from ElevenLabs';
COMMENT ON COLUMN client_interviews.officer_name IS 'Name of the officer conducting the interview';
COMMENT ON COLUMN client_interviews.officer_email IS 'Email address of the officer conducting the interview';
COMMENT ON COLUMN client_interviews.client_account_id IS 'Account ID of the client being interviewed';
COMMENT ON COLUMN client_interviews.minio_audio_url IS 'URL to the audio recording stored in MinIO';
COMMENT ON COLUMN client_interviews.minio_transcript_url IS 'URL to the conversation transcript stored in MinIO';
COMMENT ON COLUMN client_interviews.minio_report_url IS 'URL to the generated PDF report stored in MinIO';
COMMENT ON COLUMN client_interviews.interview_date IS 'Date and time when the interview was conducted';
COMMENT ON COLUMN client_interviews.status IS 'Current status of the interview (completed, processing, failed)';
COMMENT ON COLUMN client_interviews.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN client_interviews.updated_at IS 'Timestamp when the record was last updated';

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_client_interviews_account_id ON client_interviews(client_account_id);
CREATE INDEX IF NOT EXISTS idx_client_interviews_officer_email ON client_interviews(officer_email);
CREATE INDEX IF NOT EXISTS idx_client_interviews_date ON client_interviews(interview_date);
CREATE INDEX IF NOT EXISTS idx_client_interviews_status ON client_interviews(status);
CREATE INDEX IF NOT EXISTS idx_client_interviews_conversation_id ON client_interviews(conversation_id);

-- Add comments to indexes
COMMENT ON INDEX idx_client_interviews_account_id IS 'Index for querying interviews by client account ID';
COMMENT ON INDEX idx_client_interviews_officer_email IS 'Index for querying interviews by officer email';
COMMENT ON INDEX idx_client_interviews_date IS 'Index for querying interviews by date range';
COMMENT ON INDEX idx_client_interviews_status IS 'Index for querying interviews by status';
COMMENT ON INDEX idx_client_interviews_conversation_id IS 'Index for querying interviews by conversation ID';

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_client_interviews_updated_at 
    BEFORE UPDATE ON client_interviews 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add some sample data for testing (optional)
-- INSERT INTO client_interviews (conversation_id, officer_name, officer_email, client_account_id, status) 
-- VALUES 
--     ('test_conv_001', 'John Doe', 'john.doe@bionicaisolutions.com', 'acc123', 'completed'),
--     ('test_conv_002', 'Jane Smith', 'jane.smith@bionicaisolutions.com', 'acc456', 'completed');

-- Grant necessary permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON client_interviews TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE client_interviews_id_seq TO your_app_user; 
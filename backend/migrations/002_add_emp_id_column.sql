-- Migration: 002_add_emp_id_column.sql
-- Description: Add emp_id column to conversation tables for employee identification
-- Created: 2025-01-27
-- Dependencies: 001_create_postprocess_tables.sql

-- Add emp_id column to conversation_runs table
-- This table stores individual conversation run records
ALTER TABLE conversation_runs ADD COLUMN IF NOT EXISTS emp_id TEXT;

-- Add index for emp_id column to improve query performance
CREATE INDEX IF NOT EXISTS idx_conversation_runs_emp_id ON conversation_runs(emp_id);

-- Add emp_id column to conversation_processing table
-- This table stores conversation processing job records
ALTER TABLE conversation_processing ADD COLUMN IF NOT EXISTS emp_id TEXT;

-- Add index for emp_id column to improve query performance
CREATE INDEX IF NOT EXISTS idx_conversation_processing_emp_id ON conversation_processing(emp_id);

-- Add emp_id column to conversation_files table
-- This table stores file information for conversations
ALTER TABLE conversation_files ADD COLUMN IF NOT EXISTS emp_id TEXT;

-- Add index for emp_id column to improve query performance
CREATE INDEX IF NOT EXISTS idx_conversation_files_emp_id ON conversation_files(emp_id);

-- Add emp_id column to processing_audit_log table
-- This table stores audit logs for processing operations
ALTER TABLE processing_audit_log ADD COLUMN IF NOT EXISTS emp_id TEXT;

-- Add index for emp_id column to improve query performance
CREATE INDEX IF NOT EXISTS idx_processing_audit_log_emp_id ON processing_audit_log(emp_id);

-- Add comments for documentation
COMMENT ON COLUMN conversation_runs.emp_id IS 'Employee identifier within the account';
COMMENT ON COLUMN conversation_processing.emp_id IS 'Employee identifier for the processing job';
COMMENT ON COLUMN conversation_files.emp_id IS 'Employee identifier for the file';
COMMENT ON COLUMN processing_audit_log.emp_id IS 'Employee identifier for the audit log entry';

-- Verify the changes
DO $$
BEGIN
    -- Check if emp_id columns were added successfully
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversation_runs' AND column_name = 'emp_id'
    ) THEN
        RAISE EXCEPTION 'emp_id column not found in conversation_runs table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversation_processing' AND column_name = 'emp_id'
    ) THEN
        RAISE EXCEPTION 'emp_id column not found in conversation_processing table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversation_files' AND column_name = 'emp_id'
    ) THEN
        RAISE EXCEPTION 'emp_id column not found in conversation_files table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'processing_audit_log' AND column_name = 'emp_id'
    ) THEN
        RAISE EXCEPTION 'emp_id column not found in processing_audit_log table';
    END IF;
    
    -- Check if indexes were created successfully
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_conversation_runs_emp_id'
    ) THEN
        RAISE EXCEPTION 'emp_id index not found in conversation_runs table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_conversation_processing_emp_id'
    ) THEN
        RAISE EXCEPTION 'emp_id index not found in conversation_processing table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_conversation_files_emp_id'
    ) THEN
        RAISE EXCEPTION 'emp_id index not found in conversation_files table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_processing_audit_log_emp_id'
    ) THEN
        RAISE EXCEPTION 'emp_id index not found in processing_audit_log table';
    END IF;
    
    RAISE NOTICE 'Migration 002_add_emp_id_column completed successfully';
END $$;

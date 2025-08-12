#!/bin/bash

# Database Tables Setup Script
# This script sets up the database tables for the FedFina application

set -e

echo "🗄️ Setting up Database Tables..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

NAMESPACE=${1:-fedfina}

# Step 1: Try to create tables using the backend pod
print_status "Attempting to create database tables using backend pod..."

BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=fedfina-backend -o jsonpath='{.items[0].metadata.name}')

if [ -n "$BACKEND_POD" ]; then
    print_status "Using backend pod: $BACKEND_POD"
    
    # Create tables using Python script
    kubectl exec $BACKEND_POD -n $NAMESPACE -- python3 -c "
import psycopg2
import os
import sys

try:
    # Get database connection details from environment
    db_url = os.environ.get('DATABASE_URL')
    print('Connecting to database...')
    
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Create tables
    print('Creating conversation_processing table...')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_processing (
            id SERIAL PRIMARY KEY,
            processing_id VARCHAR(255) UNIQUE NOT NULL,
            conversation_id VARCHAR(255) NOT NULL,
            email_id VARCHAR(255) NOT NULL,
            account_id VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending' NOT NULL,
            progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
            current_step VARCHAR(100),
            error_message TEXT,
            processing_started_at TIMESTAMP,
            processing_completed_at TIMESTAMP,
            estimated_completion TIMESTAMP,
            total_duration INTERVAL,
            minio_transcript_url TEXT,
            minio_audio_url TEXT,
            minio_report_url TEXT,
            openai_summary TEXT,
            summary_topic VARCHAR(255),
            summary_sentiment VARCHAR(50),
            summary_key_points JSONB,
            summary_action_items JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    print('Creating conversation_files table...')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_files (
            id SERIAL PRIMARY KEY,
            conversation_id VARCHAR(255) NOT NULL,
            account_id VARCHAR(255) NOT NULL,
            file_type VARCHAR(50) NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_size BIGINT,
            minio_path TEXT NOT NULL,
            minio_url TEXT,
            url_expires_at TIMESTAMP,
            content_type VARCHAR(100),
            checksum VARCHAR(64),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    print('Creating processing_audit_log table...')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processing_audit_log (
            id SERIAL PRIMARY KEY,
            processing_id VARCHAR(255) NOT NULL,
            conversation_id VARCHAR(255) NOT NULL,
            account_id VARCHAR(255) NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            event_status VARCHAR(50) NOT NULL,
            step_name VARCHAR(100),
            step_duration INTERVAL,
            event_data JSONB,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    print('Creating account_settings table...')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_settings (
            id SERIAL PRIMARY KEY,
            account_id VARCHAR(255) UNIQUE NOT NULL,
            email_id VARCHAR(255) NOT NULL,
            settings JSONB DEFAULT '{}',
            preferences JSONB DEFAULT '{}',
            api_limits JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    print('Creating api_usage_metrics table...')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_usage_metrics (
            id SERIAL PRIMARY KEY,
            account_id VARCHAR(255) NOT NULL,
            api_key_hash VARCHAR(64) NOT NULL,
            endpoint VARCHAR(100) NOT NULL,
            request_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            total_duration INTERVAL,
            window_start TIMESTAMP NOT NULL,
            window_end TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    # Create indexes
    print('Creating indexes...')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_processing_conversation_id ON conversation_processing(conversation_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_processing_account_id ON conversation_processing(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_processing_status ON conversation_processing(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_processing_created_at ON conversation_processing(created_at)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_files_conversation_id ON conversation_files(conversation_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_files_account_id ON conversation_files(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_files_file_type ON conversation_files(file_type)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_processing_audit_log_processing_id ON processing_audit_log(processing_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_processing_audit_log_conversation_id ON processing_audit_log(conversation_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_processing_audit_log_event_type ON processing_audit_log(event_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_processing_audit_log_created_at ON processing_audit_log(created_at)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_settings_account_id ON account_settings(account_id)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_usage_metrics_account_id ON api_usage_metrics(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_usage_metrics_api_key_hash ON api_usage_metrics(api_key_hash)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_usage_metrics_window ON api_usage_metrics(window_start, window_end)')
    
    conn.commit()
    print('Database tables created successfully!')
    sys.exit(0)
    
except Exception as e:
    print(f'Error: {e}')
    print('Database setup failed. Manual intervention may be required.')
    print('You may need to:')
    print('1. Connect to the database as a superuser')
    print('2. Grant permissions to the fedfina user')
    print('3. Create the tables manually')
    sys.exit(1)
finally:
    if 'conn' in locals():
        conn.close()
"
    
    if [ $? -eq 0 ]; then
        print_success "Database tables created successfully!"
    else
        print_warning "Database setup failed. Manual intervention required."
        print_status "You may need to connect to the database as a superuser and grant permissions."
    fi
else
    print_error "No backend pod found"
    exit 1
fi

# Step 2: Test the setup
print_status "Testing database connection..."

kubectl exec $BACKEND_POD -n $NAMESPACE -- curl -s http://localhost:8000/api/v1/health | python3 -m json.tool 2>/dev/null || echo "Health check failed"

print_success "Database setup completed!"

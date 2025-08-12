#!/bin/bash

# Comprehensive Environment Setup Script
# This script sets up the complete environment for the FedFina application

set -e

echo "🚀 Starting comprehensive environment setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we can connect to the cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi

print_status "Connected to Kubernetes cluster"

# Step 1: Create namespace if it doesn't exist
print_status "Creating fedfina namespace..."
kubectl create namespace fedfina --dry-run=client -o yaml | kubectl apply -f -

# Step 2: Create Docker registry secret
print_status "Creating Docker registry secret..."
kubectl create secret docker-registry docker-registry-secret \
    --docker-server=docker.io \
    --docker-username=docker4zerocool \
    --docker-password="your-docker-token-here" \
    --namespace=fedfina \
    --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Create application secrets
print_status "Creating application secrets..."
kubectl apply -f deploy/secrets-production.yaml

# Step 4: Create database tables
print_status "Setting up database tables..."

# Create a temporary pod to run database migrations
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: db-setup
  namespace: fedfina
spec:
  containers:
  - name: postgres
    image: postgres:15
    command: ["/bin/bash"]
    args:
    - -c
    - |
      echo "Waiting for PostgreSQL to be ready..."
      sleep 10
      
      echo "Creating database tables..."
      PGPASSWORD='fedfinaTh1515T0p53cr3t' psql -h pg-rw.postgres -U fedfina -d fedfina << 'SQL'
      -- Create conversation_processing table
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
      );

      -- Create conversation_files table
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
      );

      -- Create processing_audit_log table
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
      );

      -- Create account_settings table
      CREATE TABLE IF NOT EXISTS account_settings (
          id SERIAL PRIMARY KEY,
          account_id VARCHAR(255) UNIQUE NOT NULL,
          email_id VARCHAR(255) NOT NULL,
          settings JSONB DEFAULT '{}',
          preferences JSONB DEFAULT '{}',
          api_limits JSONB DEFAULT '{}',
          created_at TIMESTAMP DEFAULT NOW(),
          updated_at TIMESTAMP DEFAULT NOW()
      );

      -- Create api_usage_metrics table
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
      );

      -- Create indexes
      CREATE INDEX IF NOT EXISTS idx_conversation_processing_conversation_id ON conversation_processing(conversation_id);
      CREATE INDEX IF NOT EXISTS idx_conversation_processing_account_id ON conversation_processing(account_id);
      CREATE INDEX IF NOT EXISTS idx_conversation_processing_status ON conversation_processing(status);
      CREATE INDEX IF NOT EXISTS idx_conversation_processing_created_at ON conversation_processing(created_at);
      
      CREATE INDEX IF NOT EXISTS idx_conversation_files_conversation_id ON conversation_files(conversation_id);
      CREATE INDEX IF NOT EXISTS idx_conversation_files_account_id ON conversation_files(account_id);
      CREATE INDEX IF NOT EXISTS idx_conversation_files_file_type ON conversation_files(file_type);
      
      CREATE INDEX IF NOT EXISTS idx_processing_audit_log_processing_id ON processing_audit_log(processing_id);
      CREATE INDEX IF NOT EXISTS idx_processing_audit_log_conversation_id ON processing_audit_log(conversation_id);
      CREATE INDEX IF NOT EXISTS idx_processing_audit_log_event_type ON processing_audit_log(event_type);
      CREATE INDEX IF NOT EXISTS idx_processing_audit_log_created_at ON processing_audit_log(created_at);
      
      CREATE INDEX IF NOT EXISTS idx_account_settings_account_id ON account_settings(account_id);
      
      CREATE INDEX IF NOT EXISTS idx_api_usage_metrics_account_id ON api_usage_metrics(account_id);
      CREATE INDEX IF NOT EXISTS idx_api_usage_metrics_api_key_hash ON api_usage_metrics(api_key_hash);
      CREATE INDEX IF NOT EXISTS idx_api_usage_metrics_window ON api_usage_metrics(window_start, window_end);
      
      echo "Database tables created successfully!"
SQL
      
      echo "Database setup completed!"
  restartPolicy: Never
EOF

# Wait for the database setup pod to complete
print_status "Waiting for database setup to complete..."
kubectl wait --for=condition=Ready pod/db-setup -n fedfina --timeout=300s
kubectl logs db-setup -n fedfina

# Clean up the database setup pod
kubectl delete pod db-setup -n fedfina

# Step 5: Create MinIO bucket
print_status "Setting up MinIO bucket..."

# Create a temporary pod to set up MinIO
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: minio-setup
  namespace: fedfina
spec:
  containers:
  - name: minio-client
    image: minio/mc:latest
    command: ["/bin/sh"]
    args:
    - -c
    - |
      echo "Setting up MinIO bucket..."
      
      # Configure MinIO client
      mc alias set myminio http://minio-hl.minio:9000 tr8MiSh0Y1wnXDCKnu0i yZTc7bcidna9C8sPFIGaQvR9velHh0XoUbbxuMrn
      
      # Create bucket if it doesn't exist
      mc mb myminio/fedfina-reports --ignore-existing
      
      # Set bucket policy for read/write access
      mc policy set download myminio/fedfina-reports
      
      echo "MinIO bucket setup completed!"
      
      # List buckets to verify
      echo "Available buckets:"
      mc ls myminio
  restartPolicy: Never
EOF

# Wait for the MinIO setup pod to complete
print_status "Waiting for MinIO setup to complete..."
kubectl wait --for=condition=Ready pod/minio-setup -n fedfina --timeout=300s
kubectl logs minio-setup -n fedfina

# Clean up the MinIO setup pod
kubectl delete pod minio-setup -n fedfina

# Step 6: Apply network policy for SMTP
print_status "Applying network policy for SMTP..."
kubectl apply -f deploy/network-policy-smtp.yaml

# Step 7: Deploy the application
print_status "Deploying the application..."
kubectl apply -f deploy/deployment-v2.yaml

# Step 8: Wait for pods to be ready
print_status "Waiting for pods to be ready..."
kubectl wait --for=condition=Available deployment/fedfina-backend -n fedfina --timeout=300s
kubectl wait --for=condition=Available deployment/fedfina-frontend -n fedfina --timeout=300s

# Step 9: Verify deployment
print_status "Verifying deployment..."
kubectl get pods -n fedfina

# Step 10: Test connectivity
print_status "Testing service connectivity..."

# Test backend health
BACKEND_POD=$(kubectl get pods -n fedfina -l app=fedfina-backend -o jsonpath='{.items[0].metadata.name}')
if [ -n "$BACKEND_POD" ]; then
    print_status "Testing backend health endpoint..."
    kubectl exec $BACKEND_POD -n fedfina -- curl -f http://localhost:8000/api/v1/health || print_warning "Backend health check failed"
fi

print_success "Environment setup completed!"
print_status "Application should be accessible at: http://fedfina-s.bionicaisolutions.com"
print_status "Backend API: http://fedfina-s.bionicaisolutions.com/api"
print_status "Frontend: http://fedfina-s.bionicaisolutions.com"

echo ""
print_status "Next steps:"
echo "1. Check pod logs: kubectl logs -f deployment/fedfina-backend -n fedfina"
echo "2. Test API endpoints"
echo "3. Monitor application health"

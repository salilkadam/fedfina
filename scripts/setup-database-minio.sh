#!/bin/bash

# Database and MinIO Setup Script
# This script sets up the database tables and MinIO bucket for the FedFina application

set -e

echo "🔧 Setting up Database Tables and MinIO Bucket..."

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

# Check if we're in the fedfina namespace
NAMESPACE=${1:-fedfina}
print_status "Using namespace: $NAMESPACE"

# Step 1: Create MinIO bucket
print_status "Setting up MinIO bucket..."

kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: minio-setup
  namespace: $NAMESPACE
spec:
  containers:
  - name: minio-client
    image: minio/mc:latest
    command: ["/bin/sh"]
    args:
    - -c
    - |
      echo "Setting up MinIO bucket..."
      mc alias set myminio http://minio-hl.minio.svc.cluster.local:9000 tr8MiSh0Y1wnXDCKnu0i yZTc7bcidna9C8sPFIGaQvR9velHh0XoUbbxuMrn
      mc mb myminio/fedfina-reports --ignore-existing
      mc policy set download myminio/fedfina-reports
      echo "MinIO bucket setup completed!"
      mc ls myminio
  restartPolicy: Never
EOF

print_status "Waiting for MinIO setup to complete..."
kubectl wait --for=condition=Ready pod/minio-setup -n $NAMESPACE --timeout=300s
kubectl logs minio-setup -n $NAMESPACE

# Clean up MinIO setup pod
kubectl delete pod minio-setup -n $NAMESPACE

# Step 2: Create database tables
print_status "Setting up database tables..."

# Create a configmap with the migration SQL
kubectl create configmap migration-config --from-file=backend/migrations/001_create_postprocess_tables.sql -n $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Create a pod to run the migration
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: db-setup
  namespace: $NAMESPACE
spec:
  containers:
  - name: postgres
    image: postgres:15
    command: ["/bin/bash"]
    args:
    - -c
    - |
      echo "Setting up database tables..."
      echo "Note: This may fail due to permissions. Manual setup may be required."
      PGPASSWORD='fedfinaTh1515T0p53cr3t' psql -h pg-rw.postgres.svc.cluster.local -U fedfina -d fedfina -f /tmp/001_create_postprocess_tables.sql || echo "Database setup failed - manual intervention required"
    volumeMounts:
    - name: migration-sql
      mountPath: /tmp
  volumes:
  - name: migration-sql
    configMap:
      name: migration-config
  restartPolicy: Never
EOF

print_status "Waiting for database setup to complete..."
kubectl wait --for=condition=Ready pod/db-setup -n $NAMESPACE --timeout=300s
kubectl logs db-setup -n $NAMESPACE

# Clean up database setup pod
kubectl delete pod db-setup -n $NAMESPACE
kubectl delete configmap migration-config -n $NAMESPACE

# Step 3: Test the setup
print_status "Testing setup..."

# Get a backend pod name
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=fedfina-backend -o jsonpath='{.items[0].metadata.name}')

if [ -n "$BACKEND_POD" ]; then
    print_status "Testing backend health endpoint..."
    kubectl exec $BACKEND_POD -n $NAMESPACE -- curl -s http://localhost:8000/api/v1/health | python3 -m json.tool 2>/dev/null || echo "Health check failed"
else
    print_error "No backend pod found"
fi

print_success "Setup completed!"
print_status "Next steps:"
echo "1. If database tables failed to create, you may need to manually grant permissions"
echo "2. Update OpenAI API key in secrets if needed"
echo "3. Test the application endpoints"

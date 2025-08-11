# FedFina Deployment Summary

## 🎯 **Deployment Configuration**

### **Cluster Setup**
- **Type**: Internal K3s cluster (no internet access)
- **Existing Services**: PostgreSQL, Redis, MinIO already deployed
- **Access**: Internal cluster networking only

### **Connection Details**

#### **Database (PostgreSQL)**
- **URL**: `postgresql://user:password@pg-rw.postgres.cluster.local:5432/fedfina`
- **Service**: Uses existing PostgreSQL cluster service
- **No additional pods**: Reuses existing database infrastructure

#### **Redis**
- **URL**: `redis://redis.redis.cluster.local:6379`
- **Service**: Uses existing Redis cluster service
- **No additional pods**: Reuses existing Redis infrastructure

#### **MinIO (Object Storage)**
- **Endpoint**: `minio-hl.minio.cluster.local:9000`
- **Access Key**: `tr8MiSh0Y1wnXDCKnu0i`
- **Secret Key**: `yZTc7bcidna9C8sPFIGaQvR9velHh0XoUbbxuMrn`
- **Service**: Uses existing MinIO cluster service
- **No additional pods**: Reuses existing MinIO infrastructure

#### **Email (SMTP)**
- **Server**: `smtp.gmail.com`
- **Port**: `465` (SSL)
- **Username**: `Salil.Kadam@gmail.com`
- **Use TLS**: `true`

### **FedFina Application Pods**

#### **Backend Pod**
- **Image**: `docker.io/docker4zerocool/fedfina-backend:latest`
- **Replicas**: 2
- **Port**: 8000
- **Resources**: 200m-1000m CPU, 256Mi-1Gi Memory
- **Health Check**: `/api/v1/health`

#### **Frontend Pod**
- **Image**: `docker.io/docker4zerocool/fedfina-frontend:latest`
- **Replicas**: 2
- **Port**: 3000
- **Resources**: 100m-500m CPU, 128Mi-512Mi Memory
- **Health Check**: `/`

### **Services**

#### **Backend Service**
- **Type**: ClusterIP
- **Port**: 8000
- **Internal Access**: `fedfina-backend.fedfina.svc.cluster.local:8000`

#### **Frontend Service**
- **Type**: ClusterIP
- **Port**: 3000
- **Internal Access**: `fedfina-frontend.fedfina.svc.cluster.local:3000`

### **Ingress**
- **Host**: `fedfina-s.bionicaisolutions.com`
- **Type**: Internal nginx ingress
- **SSL**: Disabled (internal cluster)
- **Routes**:
  - `/` → Frontend service
  - `/api` → Backend service

## 🔐 **Secrets Management**

All sensitive data is stored in Kubernetes secrets:
- API keys (OpenAI, ElevenLabs)
- Database credentials
- MinIO credentials
- SMTP credentials
- Redis URL

## 🌐 **Access Points**

### **Internal Cluster Access**
- **Backend API**: `http://fedfina-backend.fedfina.svc.cluster.local:8000`
- **Frontend**: `http://fedfina-frontend.fedfina.svc.cluster.local:3000`

### **Port Forwarding (for external access)**
```bash
# Backend API
kubectl port-forward -n fedfina svc/fedfina-backend 8000:8000

# Frontend
kubectl port-forward -n fedfina svc/fedfina-frontend 3000:3000
```

### **Internal DNS (if configured)**
- **Frontend**: `http://fedfina-s.bionicaisolutions.com`
- **API**: `http://fedfina-s.bionicaisolutions.com/api`

## 🚀 **Deployment Commands**

### **Manual Deployment**
```bash
./scripts/deploy-to-k3s.sh
```

### **CI/CD Deployment**
```bash
git push origin main  # Triggers automatic deployment
```

## 🔍 **Verification Commands**

```bash
# Check pods
kubectl get pods -n fedfina

# Check services
kubectl get services -n fedfina

# Check secrets
kubectl get secrets -n fedfina

# Health checks
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
  curl -f http://fedfina-backend.fedfina.svc.cluster.local:8000/api/v1/health

# Logs
kubectl logs -n fedfina -l app=fedfina-backend
kubectl logs -n fedfina -l app=fedfina-frontend
```

## 📊 **Resource Usage**

### **Backend**
- **Requests**: 200m CPU, 256Mi Memory
- **Limits**: 1000m CPU, 1Gi Memory

### **Frontend**
- **Requests**: 100m CPU, 128Mi Memory
- **Limits**: 500m CPU, 512Mi Memory

## 🔒 **Security Notes**

1. **Internal Only**: No internet exposure
2. **Secrets**: All credentials in Kubernetes secrets
3. **Network**: ClusterIP services (internal access only)
4. **Existing Infrastructure**: Reuses PostgreSQL, Redis, MinIO

## 📝 **Key Differences from Standard Deployment**

1. **No Database Pods**: Uses existing PostgreSQL cluster
2. **No Redis Pods**: Uses existing Redis cluster
3. **No MinIO Pods**: Uses existing MinIO cluster
4. **Internal Access**: No internet exposure
5. **Updated Endpoints**: Uses cluster-specific service names

# FedFina K3s Deployment Guide

This guide covers deploying FedFina to a private K3s cluster with Docker Hub images.

## Prerequisites

### 1. K3s Cluster Setup
- K3s cluster running and accessible
- kubectl configured to connect to your cluster
- NGINX Ingress Controller installed
- Cert-Manager (optional, for SSL certificates)

### 2. Docker Hub Access
- Docker Hub account with repository access
- Docker Hub access token for CI/CD

### 3. Required Secrets
- OpenAI API Key
- ElevenLabs API Key
- SMTP credentials
- Database connection details

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (React)       │    │   (FastAPI)     │    │   Services      │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   NGINX         │
                    │   Ingress       │
                    │   Controller    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   fedfina-s.    │
                    │   bionicaisolu- │
                    │   tions.com     │
                    └─────────────────┘
```

## Deployment Steps

### Step 1: Setup Docker Registry Secrets

Create Docker Hub registry secrets for image pulling:

```bash
# Set your Docker Hub credentials
export DOCKER_USERNAME="your-dockerhub-username"
export DOCKER_PASSWORD="your-dockerhub-token"
export DOCKER_EMAIL="your-email@example.com"

# Run the secrets setup script
./scripts/setup-k3s-secrets.sh all
```

### Step 2: Configure Application Secrets

Update the secrets file with your actual values:

```bash
# Edit the secrets file
nano deploy/secrets.yaml
```

Replace the base64 encoded values with your actual secrets:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: fedfina-secrets
  namespace: fedfina
type: Opaque
data:
  # Base64 encode your actual values
  api-secret-key: <base64-encoded-api-secret>
  database-url: <base64-encoded-database-url>
  openai-api-key: <base64-encoded-openai-key>
  elevenlabs-api-key: <base64-encoded-elevenlabs-key>
  # ... other secrets
```

### Step 3: Deploy to Staging

```bash
# Deploy staging environment
kubectl apply -f deploy/deployment-staging.yaml

# Check deployment status
kubectl get pods -n fedfina-staging
kubectl get services -n fedfina-staging
kubectl get ingress -n fedfina-staging
```

### Step 4: Deploy to Production

```bash
# Deploy production environment
kubectl apply -f deploy/deployment-v2.yaml

# Check deployment status
kubectl get pods -n fedfina
kubectl get services -n fedfina
kubectl get ingress -n fedfina
```

## CI/CD Pipeline

### GitHub Actions Setup

1. **Repository Secrets**: Add the following secrets to your GitHub repository:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub access token
   - `K3S_CONFIG`: Base64 encoded kubeconfig file

2. **Environment Protection**: Set up environment protection rules for staging and production

3. **Workflow Triggers**:
   - Push to `develop` branch → Deploy to staging
   - Push to `main` branch → Deploy to production
   - Manual trigger via GitHub Actions UI

### Pipeline Flow

```
Code Push → Tests → Build Images → Push to Docker Hub → Deploy to K3s
```

## Accessing the Application

### Internal Access

Since your K3s cluster is private, access the application through:

1. **Port Forwarding**:
   ```bash
   # Frontend
   kubectl port-forward -n fedfina svc/fedfina-frontend 3000:3000
   
   # Backend
   kubectl port-forward -n fedfina svc/fedfina-backend 8000:8000
   ```

2. **Internal DNS**: If you have internal DNS setup:
   - Frontend: `http://fedfina-s.bionicaisolutions.com`
   - API: `http://fedfina-s.bionicaisolutions.com/api`

3. **Cluster IP Access**:
   - Frontend: `fedfina-frontend.fedfina.svc.cluster.local:3000`
   - Backend: `fedfina-backend.fedfina.svc.cluster.local:8000`

### Health Checks

```bash
# Check application health
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
  curl -f http://fedfina-backend.fedfina.svc.cluster.local:8000/api/v1/health

# Check frontend
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
  curl -f http://fedfina-frontend.fedfina.svc.cluster.local:3000/
```

## Monitoring and Logs

### View Logs

```bash
# Backend logs
kubectl logs -n fedfina -l app=fedfina-backend -f

# Frontend logs
kubectl logs -n fedfina -l app=fedfina-frontend -f

# All logs in namespace
kubectl logs -n fedfina --all-containers=true -f
```

### Check Resource Usage

```bash
# Pod status
kubectl get pods -n fedfina

# Resource usage
kubectl top pods -n fedfina

# Service endpoints
kubectl get endpoints -n fedfina
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**:
   ```bash
   # Check if Docker registry secret exists
   kubectl get secret docker-registry-secret -n fedfina
   
   # Recreate if needed
   kubectl delete secret docker-registry-secret -n fedfina
   ./scripts/setup-k3s-secrets.sh production
   ```

2. **Pod Startup Issues**:
   ```bash
   # Check pod events
   kubectl describe pod <pod-name> -n fedfina
   
   # Check pod logs
   kubectl logs <pod-name> -n fedfina
   ```

3. **Ingress Issues**:
   ```bash
   # Check ingress status
   kubectl get ingress -n fedfina
   kubectl describe ingress fedfina-ingress -n fedfina
   
   # Check NGINX controller logs
   kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
   ```

### Scaling

```bash
# Scale backend
kubectl scale deployment fedfina-backend -n fedfina --replicas=3

# Scale frontend
kubectl scale deployment fedfina-frontend -n fedfina --replicas=2
```

## Security Considerations

1. **Network Policies**: Implement network policies to restrict pod-to-pod communication
2. **RBAC**: Use appropriate service accounts and role bindings
3. **Secrets Management**: Consider using external secret management solutions
4. **Image Security**: Scan images for vulnerabilities before deployment

## Backup and Recovery

### Database Backup

```bash
# Create database backup
kubectl exec -n fedfina <postgres-pod> -- pg_dump -U user fedfina > backup.sql

# Restore database
kubectl exec -i -n fedfina <postgres-pod> -- psql -U user fedfina < backup.sql
```

### Configuration Backup

```bash
# Export current configuration
kubectl get all -n fedfina -o yaml > fedfina-backup.yaml
kubectl get secrets -n fedfina -o yaml > fedfina-secrets-backup.yaml
```

## Maintenance

### Rolling Updates

```bash
# Trigger rolling update
kubectl set image deployment/fedfina-backend backend=docker.io/docker4zerocool/fedfina-backend:new-tag -n fedfina

# Monitor rollout
kubectl rollout status deployment/fedfina-backend -n fedfina
```

### Cleanup

```bash
# Remove deployment
kubectl delete -f deploy/deployment-v2.yaml

# Remove secrets
kubectl delete secret docker-registry-secret -n fedfina
kubectl delete secret fedfina-secrets -n fedfina

# Remove namespace
kubectl delete namespace fedfina
```

## Support

For issues and questions:
1. Check the logs and events
2. Review the troubleshooting section
3. Check GitHub Issues for known problems
4. Contact the development team

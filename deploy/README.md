# FedFina K3s Deployment

This directory contains the Kubernetes deployment files for FedFina application.

## 🚀 Quick Deploy

```bash
# Deploy to K3s
./scripts/deploy-k3s.sh

# Or specify namespace
./scripts/deploy-k3s.sh my-namespace
```

## 📁 Files

- `deployment-v2.yaml` - Main deployment with frontend, backend, services, and ingress
- `secrets.yaml` - Kubernetes secrets template (update with your actual secrets)
- `deployment.yaml` - Original deployment (legacy)

## 🔧 Configuration

### Docker Images
- Backend: `docker.io/docker4zerocool/fedfina-backend:latest`
- Frontend: `docker.io/docker4zerocool/fedfina-frontend:latest`

### Ingress Domain
- **New Domain**: `fedfina-s.bionicaisolutions.com`
- **Frontend**: https://fedfina-s.bionicaisolutions.com
- **Backend API**: https://fedfina-s.bionicaisolutions.com/api

## 🔐 Secrets

Update `secrets.yaml` with your actual base64 encoded secrets:

```bash
# Example: encode your secrets
echo -n "your-actual-secret" | base64
```

Required secrets:
- `api-secret-key` - API secret key
- `database-url` - PostgreSQL connection string
- `openai-api-key` - OpenAI API key
- `elevenlabs-api-key` - ElevenLabs API key
- `elevenlabs-webhook-secret` - ElevenLabs webhook secret
- `minio-access-key` - MinIO access key
- `minio-secret-key` - MinIO secret key
- `smtp-server` - SMTP server
- `smtp-username` - SMTP username
- `smtp-password` - SMTP password
- `smtp-from-email` - SMTP from email

## 📊 Monitoring

```bash
# Check deployment status
kubectl get pods -n fedfina

# View logs
kubectl logs -f deployment/fedfina-backend -n fedfina
kubectl logs -f deployment/fedfina-frontend -n fedfina

# Check ingress
kubectl describe ingress fedfina-ingress -n fedfina

# Check services
kubectl get services -n fedfina
```

## 🔄 Updates

To update the deployment:

1. Push new Docker images:
```bash
./scripts/docker-hub-push.sh docker4zerocool
```

2. Restart deployments:
```bash
kubectl rollout restart deployment/fedfina-backend -n fedfina
kubectl rollout restart deployment/fedfina-frontend -n fedfina
```

## 🏗️ Architecture

```
Internet → Ingress → Frontend Service → Frontend Pod
                ↓
            Backend Service → Backend Pod
```

- **Frontend**: React app served by Nginx
- **Backend**: FastAPI application
- **Ingress**: Nginx ingress controller with SSL
- **Secrets**: Kubernetes secrets for sensitive data
- **Health Checks**: Liveness and readiness probes

## 🔍 Troubleshooting

### Common Issues

1. **Images not found**: Ensure Docker images are pushed to Docker Hub
2. **Secrets not found**: Check that secrets.yaml is applied
3. **Ingress not working**: Verify cert-manager and nginx-ingress are installed
4. **Health checks failing**: Check application logs for errors

### Debug Commands

```bash
# Check pod status
kubectl describe pod <pod-name> -n fedfina

# Check events
kubectl get events -n fedfina --sort-by='.lastTimestamp'

# Check ingress status
kubectl describe ingress fedfina-ingress -n fedfina

# Check certificate status
kubectl get certificates -n fedfina
``` 
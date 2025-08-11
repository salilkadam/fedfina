# FedFina CI/CD Setup Guide

## 🚀 Overview

This guide will help you set up Continuous Integration and Continuous Deployment (CI/CD) for the FedFina application using GitHub Actions and K3s.

## 📋 Prerequisites

### 1. GitHub Repository
- ✅ Repository is already set up at `https://github.com/salilkadam/fedfina`
- ✅ Code is committed and pushed to the `main` branch

### 2. Docker Hub Account
- Create a Docker Hub account at https://hub.docker.com
- Create a Personal Access Token (PAT) for CI/CD

### 3. K3s Cluster
- ✅ K3s cluster is running and accessible
- ✅ `kubectl` is configured to connect to your cluster

## 🔧 Required GitHub Secrets

You need to add these secrets to your GitHub repository:

### 1. Go to GitHub Repository Settings
- Navigate to: `https://github.com/salilkadam/fedfina/settings/secrets/actions`
- Click "New repository secret"

### 2. Add the following secrets:

| Secret Name | Description | Value |
|-------------|-------------|-------|
| `DOCKER_USERNAME` | Your Docker Hub username | `your-dockerhub-username` |
| `DOCKER_PASSWORD` | Your Docker Hub Personal Access Token | `your-dockerhub-pat` |
| `K3S_CONFIG` | Base64 encoded kubeconfig | `echo -n "$(cat ~/.kube/config)" \| base64` |

### 3. How to get K3S_CONFIG:
```bash
# On your machine with kubectl access to K3s
echo -n "$(cat ~/.kube/config)" | base64
# Copy the output and paste it as the K3S_CONFIG secret value
```

## 🐳 Docker Hub Setup

### 1. Create Personal Access Token
1. Go to Docker Hub → Account Settings → Security
2. Click "New Access Token"
3. Give it a name like "FedFina CI/CD"
4. Copy the token (you'll need it for the DOCKER_PASSWORD secret)

### 2. Create Repository (if needed)
- The CI/CD expects images at:
  - `docker.io/docker4zerocool/fedfina-backend`
  - `docker.io/docker4zerocool/fedfina-frontend`
- If these don't exist, create them or update the workflow

## 🔄 CI/CD Workflow

### Automatic Triggers
- **Push to `main`**: Deploys to production
- **Push to `develop`**: Deploys to staging
- **Manual trigger**: Choose environment

### Workflow Steps
1. **Test**: Runs backend and frontend tests
2. **Build**: Creates Docker images for both platforms (amd64, arm64)
3. **Push**: Pushes images to Docker Hub
4. **Deploy**: Deploys to K3s cluster

## 🚀 Deployment Process

### 1. Manual Deployment (Recommended for first time)
```bash
# Run the deployment script
./scripts/deploy-to-k3s.sh
```

### 2. Automatic Deployment via CI/CD
1. Push changes to `main` branch
2. GitHub Actions will automatically:
   - Build Docker images
   - Push to Docker Hub
   - Deploy to K3s production

### 3. Staging Deployment
```bash
# Push to develop branch for staging deployment
git checkout develop
git merge main
git push origin develop
```

## 🔍 Verification

### 1. Check Deployment Status
```bash
# Check pods
kubectl get pods -n fedfina

# Check services
kubectl get services -n fedfina

# Check ingress
kubectl get ingress -n fedfina
```

### 2. Health Checks
```bash
# Backend health
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
  curl -f http://fedfina-backend.fedfina.svc.cluster.local:8000/api/v1/health

# Frontend health
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
  curl -f http://fedfina-frontend.fedfina.svc.cluster.local:3000/
```

### 3. Logs
```bash
# Backend logs
kubectl logs -n fedfina -l app=fedfina-backend

# Frontend logs
kubectl logs -n fedfina -l app=fedfina-frontend
```

## 🌐 Access Points

### Internal Cluster Access
- **Backend API**: `http://fedfina-backend.fedfina.svc.cluster.local:8000`
- **Frontend**: `http://fedfina-frontend.fedfina.svc.cluster.local:3000`

### External Access (if DNS configured)
- **Frontend**: `http://fedfina-s.bionicaisolutions.com`
- **API**: `http://fedfina-s.bionicaisolutions.com/api`

## 🔧 Troubleshooting

### Common Issues

1. **Image Pull Errors**
   ```bash
   # Check if Docker registry secret exists
   kubectl get secrets -n fedfina
   
   # Recreate if needed
   kubectl create secret docker-registry docker-registry-secret \
     --docker-server=docker.io \
     --docker-username="your-username" \
     --docker-password="your-pat" \
     --namespace=fedfina
   ```

2. **Pod Startup Issues**
   ```bash
   # Check pod events
   kubectl describe pod <pod-name> -n fedfina
   
   # Check logs
   kubectl logs <pod-name> -n fedfina
   ```

3. **Health Check Failures**
   ```bash
   # Check if services are running
   kubectl get endpoints -n fedfina
   
   # Test connectivity
   kubectl run test --image=curlimages/curl -i --rm --restart=Never -- \
     curl -v http://fedfina-backend.fedfina.svc.cluster.local:8000/api/v1/health
   ```

## 📊 Monitoring

### 1. Resource Usage
```bash
# Check resource usage
kubectl top pods -n fedfina
kubectl top nodes
```

### 2. Scaling
```bash
# Scale backend
kubectl scale deployment fedfina-backend --replicas=3 -n fedfina

# Scale frontend
kubectl scale deployment fedfina-frontend --replicas=3 -n fedfina
```

## 🔒 Security Notes

1. **Secrets**: All sensitive data is stored in Kubernetes secrets
2. **Network**: Services are ClusterIP (internal access only)
3. **Images**: Pulled from Docker Hub with authentication
4. **RBAC**: Consider implementing proper RBAC for production

## 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Review Kubernetes events and logs
3. Verify all secrets are correctly set
4. Ensure cluster connectivity

---

**Next Steps**: Set up the GitHub secrets and run the deployment script!

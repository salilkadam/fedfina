# GitHub Secrets Configuration for FedFina CI/CD

This document outlines the required GitHub secrets for the CI/CD pipeline to work with ArgoCD.

## Required Secrets

### Docker Hub Credentials
- `dockerhub_username`: Your Docker Hub username (e.g., `docker4zerocool`)
- `dockerhub_token`: Your Docker Hub Personal Access Token (PAT)

### ArgoCD Credentials
- `ARGOCD_SERVER`: ArgoCD server URL (e.g., `https://argocd.bionicaisolutions.com`)
- `ARGOCD_USERNAME`: ArgoCD username (usually `admin`)
- `ARGOCD_PASSWORD`: ArgoCD admin password
- `ARGOCD_WEBHOOK_URL`: (Optional) ArgoCD webhook URL for automatic sync

### Notification (Optional)
- `SLACK_WEBHOOK`: Slack webhook URL for deployment notifications

## How to Set Up Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with the exact name and value

## Getting ArgoCD Password

To get your ArgoCD admin password, run:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## ArgoCD Server URL

Your ArgoCD server should be accessible at:
- Internal: `https://argocd-server.argocd.svc.cluster.local`
- External: `https://argocd.bionicaisolutions.com` (or your configured domain)

## Webhook Configuration

To set up automatic sync on git push:

1. In ArgoCD UI, go to Settings → Repositories
2. Add your repository if not already added
3. Go to Settings → Webhooks
4. Add a webhook with:
   - URL: `https://argocd-webhook.bionicaisolutions.com/api/webhook`
   - Secret: (optional, but recommended)
   - Events: Push events

## Testing the Setup

After setting up the secrets, you can test the pipeline by:

1. Making a small change to the code
2. Committing and pushing to the `main` branch
3. Checking the Actions tab in GitHub
4. Monitoring the ArgoCD UI for deployment status

## Troubleshooting

### Common Issues

1. **ArgoCD Login Failed**: Check if the server URL and credentials are correct
2. **Docker Push Failed**: Verify Docker Hub credentials and repository permissions
3. **Sync Failed**: Check if the ArgoCD application is properly configured
4. **Webhook Not Working**: Verify the webhook URL and ArgoCD webhook configuration

### Logs and Debugging

- GitHub Actions logs: Repository → Actions → Select workflow run
- ArgoCD logs: `kubectl logs -n argocd deployment/argocd-server`
- Application logs: `kubectl logs -n fedfina deployment/fedfina-backend`

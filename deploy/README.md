# fedfina React App - Kubernetes & ArgoCD Deployment

This directory contains Kubernetes manifests and ArgoCD configuration for deploying the ElevenLabs Convai React app to a cluster using ArgoCD and GitHub Actions.

## Components

- **deployment.yaml**: Kubernetes Deployment, Service, and HTTPS Ingress for the app.
- **argocd-app.yaml**: ArgoCD Application manifest for automated GitOps deployment.
- **GitHub Actions**: Workflow in `.github/workflows/deploy.yml` builds and pushes Docker images to DockerHub, then updates the deployment manifest for ArgoCD auto-sync.

## Deployment Flow

1. **Push to main**: Triggers GitHub Actions to build and push the Docker image to DockerHub, then updates the image tag in `deployment.yaml`.
2. **ArgoCD**: Watches this repo and auto-syncs the manifests to your Kubernetes cluster in the `fedfina` namespace.
3. **Ingress**: App is exposed at `https://fedfina.bionicaisolutions.com` with TLS via cert-manager (letsencrypt-prod).

## Prerequisites
- Kubernetes cluster with NGINX Ingress and cert-manager installed
- ArgoCD installed and configured
- DockerHub credentials set as GitHub secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
- DNS for `fedfina.bionicaisolutions.com` pointing to your ingress controller

## Usage
- Edit manifests as needed for your environment
- Apply `argocd-app.yaml` to your ArgoCD instance to bootstrap the app

--- 
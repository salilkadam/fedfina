# FedFina Ingress Domain Update Summary

**Date:** $(date)
**Change:** Update ingress domain from `fedfina-s.bionicaisolutions.com` to `fedfina.bionicaisolutions.com`

## Changes Made

### 1. Updated Frontend Environment Variable
**File:** `deploy/deployment-v2.yaml`
**Line:** ~150
**Change:** 
```yaml
# Before
- name: REACT_APP_API_URL
  value: "http://fedfina-s.bionicaisolutions.com/api"

# After  
- name: REACT_APP_API_URL
  value: "http://fedfina.bionicaisolutions.com/api"
```

### 2. Updated Ingress Host Configuration
**File:** `deploy/deployment-v2.yaml`
**Line:** ~200
**Change:**
```yaml
# Before
- host: fedfina-s.bionicaisolutions.com

# After
- host: fedfina.bionicaisolutions.com
```

### 3. Updated Ingress Comment
**File:** `deploy/deployment-v2.yaml`
**Line:** ~190
**Change:**
```yaml
# Before
# Internal Ingress for fedfina-s.bionicaisolutions.com

# After
# Internal Ingress for fedfina.bionicaisolutions.com
```

## How to Apply the Changes

### Option 1: Using the Update Script (Recommended)
```bash
# Make sure you're in the fedfina directory
cd /workspace/fedfina

# Run the update script
./update-ingress-domain.sh
```

### Option 2: Manual Application
```bash
# 1. Backup current configuration
kubectl get deployment fedfina-backend -n fedfina -o yaml > backup-backend-$(date +%Y%m%d-%H%M%S).yaml
kubectl get deployment fedfina-frontend -n fedfina -o yaml > backup-frontend-$(date +%Y%m%d-%H%M%S).yaml
kubectl get ingress fedfina-ingress -n fedfina -o yaml > backup-ingress-$(date +%Y%m%d-%H%M%S).yaml

# 2. Apply the updated configuration
kubectl apply -f deploy/deployment-v2.yaml

# 3. Wait for deployments to be ready
kubectl rollout status deployment/fedfina-backend -n fedfina --timeout=300s
kubectl rollout status deployment/fedfina-frontend -n fedfina --timeout=300s

# 4. Verify the changes
kubectl get ingress -n fedfina -o wide
kubectl describe ingress fedfina-ingress -n fedfina
```

## Verification Steps

### 1. Check Ingress Configuration
```bash
kubectl get ingress -n fedfina
kubectl describe ingress fedfina-ingress -n fedfina
```

### 2. Test New Domain
```bash
# Test frontend
curl -I http://fedfina.bionicaisolutions.com/

# Test backend API
curl http://fedfina.bionicaisolutions.com/api/v1/health
```

### 3. Check Pod Status
```bash
kubectl get pods -n fedfina
kubectl logs -n fedfina -l app=fedfina-frontend
kubectl logs -n fedfina -l app=fedfina-backend
```

## Expected Results

### Before Update
- **Frontend:** `http://fedfina-s.bionicaisolutions.com/`
- **API:** `http://fedfina-s.bionicaisolutions.com/api`

### After Update
- **Frontend:** `http://fedfina.bionicaisolutions.com/`
- **API:** `http://fedfina.bionicaisolutions.com/api`

## Rollback Instructions

If you need to rollback to the previous domain:

```bash
# Apply the backup files
kubectl apply -f backup-ingress-*.yaml
kubectl apply -f backup-backend-*.yaml
kubectl apply -f backup-frontend-*.yaml

# Wait for rollback to complete
kubectl rollout status deployment/fedfina-backend -n fedfina
kubectl rollout status deployment/fedfina-frontend -n fedfina
```

## Important Notes

1. **DNS Propagation:** The new domain may take a few minutes to propagate
2. **Backup Created:** Backup files are created before applying changes
3. **Zero Downtime:** The update should be zero-downtime with rolling updates
4. **Frontend API URL:** The frontend will now use the new domain for API calls

## Files Modified

- `deploy/deployment-v2.yaml` - Main deployment configuration
- `update-ingress-domain.sh` - Update script (created)
- `ingress-domain-update-summary.md` - This summary (created)

## Next Steps

1. Apply the changes using one of the methods above
2. Verify the new domain is working
3. Update any external references to use the new domain
4. Consider updating DNS records if needed
5. Monitor the application for any issues after the change


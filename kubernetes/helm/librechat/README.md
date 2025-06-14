# LibreChat Kubernetes Deployment Guide

This directory contains all the necessary files to deploy LibreChat on Kubernetes using Helm charts. This guide explains how everything works together, the reasoning behind each component, and documents all the troubleshooting steps and changes made during deployment.

## 📁 File Overview

### Core Configuration Files

#### `librechat-secret.yaml`
**Purpose**: Kubernetes Secret containing all environment variables from the original `.env` file
**Why**: 
- Secrets provide secure storage for sensitive data like API keys
- Kubernetes automatically handles encoding/decoding
- Can be mounted as environment variables in pods
- Separates configuration from application code
- Enables easy updates without rebuilding containers

#### `values.yaml`
**Purpose**: Helm chart configuration that defines how LibreChat should be deployed
**Why**:
- Helm uses values files to customize deployments
- Centralizes all deployment configuration in one place
- Enables easy environment-specific customizations
- Follows Kubernetes best practices for resource allocation
- Includes ingress, persistence, and service configurations

### Installation Scripts

#### `install.sh`
**Purpose**: Automated installation script for LibreChat deployment
**Why**:
- Simplifies the deployment process into a single command
- Ensures correct order of operations (secrets before deployment)
- Handles Helm repository setup automatically
- Provides consistent deployment across environments
- Includes helpful post-installation commands

### MongoDB Restoration Files

#### `mongodb-restore-final.yaml`
**Purpose**: Kubernetes Job that restores MongoDB data from backup using PVC storage
**Why**:
- Jobs are perfect for one-time tasks like data restoration
- Runs in the same cluster with network access to MongoDB
- Automatically cleans up after completion
- Uses PVC to access backup data reliably

#### `backup-receiver-pod.yaml`
**Purpose**: Temporary pod used to receive backup files via kubectl cp
**Why**:
- Provides a mount point for PVC storage
- Allows copying backup files from local machine to cluster storage
- Temporary solution when ConfigMaps are too small for large backups

#### `mongodb-backup-pvc.yaml`
**Purpose**: Persistent Volume Claim for storing backup data
**Why**:
- Provides reliable storage for backup files within the cluster
- Accessible by both copy and restore operations
- Uses NFS storage for large file support

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ai-stuff Namespace                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   LibreChat     │    │    MongoDB      │                │
│  │   Application   │◄──►│   (iSCSI)       │                │
│  │   (LoadBalancer)│    │                 │                │
│  └─────────────────┘    └─────────────────┘                │
│           ▲                       ▲                        │
│           │                       │                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  Secret Store   │    │  MeiliSearch    │                │
│  │  (API Keys)     │    │  (iSCSI)        │                │
│  └─────────────────┘    └─────────────────┘                │
│                                   ▲                        │
│                         ┌─────────────────┐                │
│                         │ Backup PVC      │                │
│                         │ (NFS)           │                │
│                         └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 🚧 Troubleshooting Journey & Changes Made

During deployment, we encountered several issues that required configuration changes. Here's a detailed breakdown:

### 1. **Pod Security Policy Issues**

**Problem**: Pod security violations due to default security contexts
**Solution**: Applied privileged pod security label to namespace
```bash
kubectl label namespace ai-stuff pod-security.kubernetes.io/enforce=privileged --overwrite
```
**Why**: The Helm chart's default security contexts didn't meet the restricted security policy requirements

### 2. **MongoDB Storage Issues with NFS**

**Problem**: MongoDB WiredTiger engine failing with "Operation not permitted" on NFS storage
**Root Cause**: MongoDB requires specific file system permissions that NFS doesn't provide by default
**Solution**: Changed MongoDB storage from `nfs-client` to `synology-iscsi`

**Changes Made in `values.yaml`:**
```yaml
# Before (failed)
mongodb:
  persistence:
    storageClass: "nfs-client"

# After (working)
mongodb:
  persistence:
    storageClass: "synology-iscsi"
```

**Why**: iSCSI provides block storage with proper file system support for database operations

### 3. **MeiliSearch Storage Optimization**

**Problem**: Database performance concerns on NFS
**Solution**: Also moved MeiliSearch to iSCSI storage
**Principle**: All databases use `synology-iscsi`, file storage uses `nfs-client`

### 4. **Service Type Configuration**

**Problem**: ClusterIP service wasn't accessible externally
**Solution**: Changed service type to LoadBalancer as requested

**Change in `values.yaml`:**
```yaml
service:
  type: LoadBalancer  # Changed from ClusterIP
```

### 5. **Network Connectivity Issues**

**Problem**: LibreChat couldn't connect to MongoDB and MeiliSearch
**Root Cause**: Environment variables pointed to localhost instead of Kubernetes services

**Changes Made in `librechat-secret.yaml`:**
```yaml
# Before (failed)
MONGO_URI: "mongodb://127.0.0.1:27017/LibreChat"
MEILI_HOST: "http://0.0.0.0:7700"

# After (working)
MONGO_URI: "mongodb://librechat-mongodb:27017/LibreChat"
MEILI_HOST: "http://librechat-meilisearch:7700"
```

**Why**: Kubernetes pods communicate via service names, not localhost

### 6. **Application Binding Issues**

**Problem**: Health checks failing because app bound to localhost only
**Root Cause**: HOST environment variable set to "localhost"

**Fix in `librechat-secret.yaml`:**
```yaml
# Before (failed health checks)
HOST: "localhost"

# After (working)
HOST: "0.0.0.0"
```

**Why**: Kubernetes health probes access pods via pod IP, not localhost

### 7. **MongoDB Backup Restoration Challenges**

**Problem**: Multiple failed approaches for backup restoration

#### Attempt 1: ConfigMap (Failed)
```bash
kubectl create configmap mongodb-backup-data --from-file="$BACKUP_DIR"
```
**Issue**: 3MB size limit exceeded by backup files

#### Attempt 2: HostPath (Failed)
```yaml
volumes:
- name: source-backup
  hostPath:
    path: /Users/gauranshmathur/Work/Homelab/migration/...
```
**Issue**: Local machine path not available on Kubernetes nodes

#### Attempt 3: kubectl cp + PVC (Success)
**Process**:
1. Created PVC with NFS storage for large file support
2. Created temporary pod with PVC mounted
3. Used `kubectl cp` to copy backup files to pod
4. Created restore job accessing same PVC

**Why This Worked**:
- PVC provides persistent storage accessible by multiple pods
- `kubectl cp` works regardless of cluster networking
- No size limitations like ConfigMaps
- Reliable for large backup files

### 8. **Security Context Adjustments**

**Problem**: Restore job failing due to security restrictions
**Solution**: Added proper security contexts to restore job:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 999
  runAsGroup: 999
  fsGroup: 999
  seccompProfile:
    type: RuntimeDefault
containers:
- securityContext:
    allowPrivilegeEscalation: false
    capabilities:
      drop: [ALL]
```

## 🔄 Final Deployment Flow

### 1. **Namespace Preparation**
```bash
kubectl label namespace ai-stuff pod-security.kubernetes.io/enforce=privileged --overwrite
```

### 2. **Secret Creation**
```bash
kubectl apply -f librechat-secret.yaml -n ai-stuff
```

### 3. **Helm Chart Installation**
```bash
./install.sh
```

### 4. **Data Restoration Process**
```bash
# Create backup PVC
kubectl apply -f mongodb-backup-pvc.yaml

# Create temporary pod for file copying
kubectl apply -f backup-receiver-pod.yaml

# Copy backup files
kubectl cp /local/backup/path/ ai-stuff/backup-receiver-pod:/backup/LibreChat/

# Run restoration job
kubectl apply -f mongodb-restore-final.yaml

# Cleanup
kubectl delete pod backup-receiver-pod
kubectl delete job mongodb-restore-job
```

## 📊 Final Results

**✅ Successfully Deployed:**
- LibreChat Application: LoadBalancer at `192.168.10.12:3080`
- MongoDB: 15,000+ documents restored across 23 collections
- MeiliSearch: Search functionality enabled
- All API keys and configurations preserved

**📈 Restored Data:**
- 685 conversations with 9,779 messages
- 2 users with 4,547 transactions
- 160 files and 101 shared links
- Custom prompts, presets, and configurations

## 🎯 Key Lessons Learned

### **Storage Class Selection Matters**
- **Databases**: Use block storage (iSCSI) for performance and compatibility
- **File Storage**: NFS works well for uploads and static files
- **Backup Storage**: NFS suitable for large temporary files

### **Network Service Names**
- Use Kubernetes service names (`service-name.namespace.svc.cluster.local`)
- Avoid localhost/127.0.0.1 in containerized environments
- Test connectivity with `kubectl exec` for debugging

### **Pod Security Contexts**
- Understand your cluster's security policies
- Configure appropriate security contexts for all workloads
- Use non-root users when possible

### **Data Migration Strategies**
- Large datasets require PVC-based approaches
- ConfigMaps have size limitations (3MB)
- `kubectl cp` is reliable for file transfers to pods

## 🚀 Quick Start

1. **Deploy LibreChat**
   ```bash
   ./install.sh
   ```

2. **Restore Data** (if migrating)
   ```bash
   kubectl apply -f mongodb-backup-pvc.yaml
   kubectl apply -f backup-receiver-pod.yaml
   kubectl cp /path/to/backup/ ai-stuff/backup-receiver-pod:/backup/LibreChat/
   kubectl apply -f mongodb-restore-final.yaml
   ```

3. **Access Application**
   ```bash
   # Direct access via LoadBalancer
   open http://192.168.10.12:3080
   ```

## 🔧 Customization Options

### **Scaling**
```yaml
deployment:
  replicas: 3  # High availability
```

### **Resource Limits**
```yaml
deployment:
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "4Gi"
      cpu: "2000m"
```

### **Storage Classes**
```yaml
# Databases (performance critical)
mongodb:
  persistence:
    storageClass: "synology-iscsi"

# File storage (cost effective)
persistence:
  uploads:
    storageClass: "nfs-client"
```

## 🔍 Monitoring & Troubleshooting

### **Check Deployment Status**
```bash
kubectl get pods -n ai-stuff
kubectl get services -n ai-stuff
kubectl get pvc -n ai-stuff
```

### **View Logs**
```bash
# Application logs
kubectl logs -n ai-stuff deployment/librechat-librechat -f

# Database logs
kubectl logs -n ai-stuff deployment/librechat-mongodb -f

# Job logs
kubectl logs -n ai-stuff job/mongodb-restore-job
```

### **Debug Network Issues**
```bash
# Test service connectivity
kubectl exec -n ai-stuff deployment/librechat-librechat -- nslookup librechat-mongodb

# Check environment variables
kubectl exec -n ai-stuff deployment/librechat-librechat -- env | grep MONGO_URI
```

### **Storage Debugging**
```bash
# Check PVC status
kubectl describe pvc -n ai-stuff

# Verify mount points
kubectl exec -n ai-stuff deployment/librechat-librechat -- df -h
```

## 🔐 Security Considerations

1. **API Keys**: Stored in Kubernetes Secrets with base64 encoding
2. **Pod Security**: Configured with non-root users and minimal capabilities
3. **Network Isolation**: Services communicate within cluster network
4. **Storage Security**: Separate storage classes for different data types
5. **Access Control**: Namespace-based isolation in `ai-stuff`

## 📚 Additional Resources

- [LibreChat Documentation](https://www.librechat.ai/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Community Helm Chart](https://github.com/bat-bs/helm-charts/tree/main/charts/librechat)

## 🤝 Contributing

To update this deployment:
1. Test changes in a development environment first
2. Document any new troubleshooting steps encountered
3. Update this README with lessons learned
4. Verify the deployment process end-to-end
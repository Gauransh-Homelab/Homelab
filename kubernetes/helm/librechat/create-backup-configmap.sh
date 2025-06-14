#!/bin/bash

# Script to create a ConfigMap with MongoDB backup data
# This approach works for smaller datasets. For larger datasets, consider using a PVC.

set -e

BACKUP_DIR="/Users/gauranshmathur/Work/Homelab/migration/LibreChat/librechat-migration/mongo-backup/LibreChat"
NAMESPACE="ai-stuff"

echo "📦 Creating ConfigMap with MongoDB backup data..."

# Using existing ai-stuff namespace
echo "🏗️ Using existing ai-stuff namespace..."

# Create ConfigMap with all BSON files
echo "🗃️ Adding BSON files to ConfigMap..."
kubectl create configmap mongodb-backup-data \
  --from-file="$BACKUP_DIR" \
  --namespace="$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ ConfigMap 'mongodb-backup-data' created successfully in namespace '$NAMESPACE'"
echo ""
echo "📋 To verify the ConfigMap:"
echo "  kubectl get configmap mongodb-backup-data -n $NAMESPACE"
echo ""
echo "🔍 To see the contents:"
echo "  kubectl describe configmap mongodb-backup-data -n $NAMESPACE"
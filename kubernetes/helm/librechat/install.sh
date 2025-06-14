#!/bin/bash

# LibreChat Helm Installation Script
# This script installs LibreChat using the community Helm chart

set -e

echo "🚀 Installing LibreChat with Helm..."

# Add the Helm repository
echo "📦 Adding LibreChat Helm repository..."
helm repo add librechat https://bat-bs.github.io/helm-charts/
helm repo update

# Using existing ai-stuff namespace
echo "🏗️ Using existing ai-stuff namespace..."

# Apply the secret first
echo "🔐 Applying LibreChat secret..."
kubectl apply -f librechat-secret.yaml -n ai-stuff

# Install LibreChat using Helm
echo "🎯 Installing LibreChat..."
helm upgrade --install librechat librechat/librechat \
  --namespace ai-stuff \
  --values values.yaml \
  --wait \
  --timeout 10m

echo "✅ LibreChat installation completed!"
echo ""
echo "📋 To check the status:"
echo "  kubectl get pods -n ai-stuff"
echo ""
echo "🌐 To access LibreChat:"
echo "  kubectl port-forward -n ai-stuff svc/librechat 3080:3080"
echo "  Then open http://localhost:3080"
echo ""
echo "🔍 To view logs:"
echo "  kubectl logs -n ai-stuff deployment/librechat -f"
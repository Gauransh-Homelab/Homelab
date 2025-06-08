# LGTM Stack Installation Guide

This guide provides step-by-step instructions to deploy the complete LGTM (Loki, Grafana, Tempo, Prometheus) observability stack on your Kubernetes homelab.

## Prerequisites

- kubectl configured and connected to your cluster
- Helm 3 installed
- MetalLB configured and running
- `synology-iscsi` StorageClass available

## Installation Steps

### 1. Create Namespace

```bash
kubectl create namespace monitoring
```

### 2. Add Helm Repositories

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

### 3. Install kube-prometheus-stack

Installs Prometheus, Grafana, and Alertmanager with all exporters:

```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values kube-prometheus-stack-values.yaml \
  --wait \
  --timeout 10m
```

### 4. Install Loki

```bash
helm install loki grafana/loki \
  --namespace monitoring \
  --values loki-values.yaml \
  --wait \
  --timeout 10m
```

### 5. Install Tempo

```bash
helm install tempo grafana/tempo \
  --namespace monitoring \
  --values tempo-values.yaml \
  --wait \
  --timeout 10m
```

## Verification

### Check Pod Status

```bash
kubectl get pods -n monitoring
```

### Check Services

```bash
kubectl get svc -n monitoring
```

### Check Persistent Volumes

```bash
kubectl get pvc -n monitoring
```

### Get Grafana LoadBalancer IP

```bash
kubectl get svc kube-prometheus-stack-grafana -n monitoring
```

## Access Information

- **Grafana**: Available via LoadBalancer IP on port 3000
  - Default credentials: `admin` / `admin123`
- **Prometheus**: Port-forward with `kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring`
- **AlertManager**: Port-forward with `kubectl port-forward svc/kube-prometheus-stack-alertmanager 9093:9093 -n monitoring`

## Upgrade Commands

### Update Repositories

```bash
helm repo update
```

### Upgrade Components

```bash
# kube-prometheus-stack
helm upgrade kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values kube-prometheus-stack-values.yaml

# Loki
helm upgrade loki grafana/loki \
  --namespace monitoring \
  --values loki-values.yaml

# Tempo
helm upgrade tempo grafana/tempo \
  --namespace monitoring \
  --values tempo-values.yaml
```

## Uninstall (if needed)

```bash
helm uninstall tempo -n monitoring
helm uninstall loki -n monitoring
helm uninstall kube-prometheus-stack -n monitoring
kubectl delete namespace monitoring
```

## Resource Summary

**Expected Pod Count**: 10-15 pods

**Storage Usage**:
- Prometheus: 50Gi
- Loki: 50Gi + 10Gi WAL
- Tempo: 20Gi
- Grafana: 10Gi
- Alertmanager: 5Gi
- **Total**: ~145Gi

**Memory Usage**:
- Prometheus: 2-4Gi
- Loki: 1-2Gi
- Tempo: 1-2Gi
- Grafana: 512Mi-1Gi
- Other components: ~2Gi
- **Total**: ~8-12Gi

## Post-Installation Notes

1. Review and adjust resource limits based on your cluster capacity
2. Update storage sizes based on your retention requirements
3. Change default Grafana credentials before production use
4. Configure alerting rules and notification channels in AlertManager
5. Data sources for Prometheus, Loki, and Tempo are pre-configured in Grafana
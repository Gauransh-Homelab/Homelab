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
  - Default username: `admin`
  - Get auto-generated password: `kubectl get secret kube-prometheus-stack-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode`
- **Prometheus**: Port-forward with `kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring`
- **AlertManager**: Port-forward with `kubectl port-forward svc/kube-prometheus-stack-alertmanager 9093:9093 -n monitoring`

### Pre-configured Data Sources

Grafana comes pre-configured with:
- **Prometheus**: Default data source for metrics
- **Loki**: Log aggregation with trace correlation
- **Tempo**: Distributed tracing with log correlation

### Pre-installed Dashboards

- Kubernetes Cluster Overview (ID: 7249)
- Node Exporter Dashboard (ID: 1860) 
- Loki Dashboard (ID: 13639)
- Tempo Dashboard (ID: 16698)

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
- Prometheus: 30Gi (15d retention, 45GB limit)
- Loki: 20Gi main + 5Gi WAL/read/backend = 35Gi total (7d retention)
- Tempo: 10Gi (3d retention)
- Grafana: 5Gi
- Alertmanager: 2Gi
- **Total**: ~72Gi

**Memory Usage**:
- Prometheus: 1-2Gi (1Gi request, 2Gi limit)
- Loki: 512Mi-1Gi (512Mi request, 1Gi limit)
- Tempo: 512Mi-1Gi (512Mi request, 1Gi limit)
- Grafana: 256-512Mi (256Mi request, 512Mi limit)
- Other components: ~1Gi
- **Total**: ~4-7Gi

**CPU Usage**:
- Prometheus: 200m-1000m
- Loki: 100-500m
- Tempo: 100-500m
- Grafana: 50-200m
- Other components: ~300m
- **Total**: ~750m-2.5 cores

## Post-Installation Notes

1. **Security**: Change auto-generated Grafana password via UI after first login
2. **Monitoring**: Prometheus rules and service monitors are pre-configured for all components
3. **Retention**: 
   - Prometheus: 15 days
   - Loki: 7 days  
   - Tempo: 3 days
4. **Ingestion Protocols**: Tempo accepts multiple formats:
   - OpenTelemetry (gRPC: 4317, HTTP: 4318)
   - Jaeger (gRPC: 14250, HTTP: 14268, UDP: 6831/6832)
   - Zipkin (HTTP: 9411)
   - OpenCensus (gRPC: 55678)
5. **Storage Class**: All components use `synology-iscsi` storage class
6. **Namespace**: All components deployed to `monitoring` namespace via override
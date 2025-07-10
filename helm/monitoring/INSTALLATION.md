# Monitoring Stack Installation Guide

This guide provides step-by-step instructions to deploy the complete monitoring stack on your Talos Linux Kubernetes homelab using kube-prometheus-stack, Loki, and Grafana Alloy.

## Architecture Overview

- **kube-prometheus-stack**: Provides Prometheus, Grafana, and AlertManager in one package
- **Loki**: Log aggregation system with 7-day retention
- **Grafana Alloy**: Unified collection agent for both metrics and logs

## Prerequisites

- kubectl configured and connected to your Talos Linux cluster
- Helm 3 installed
- `synology-iscsi` StorageClass available
- Minimum 6GB RAM available for monitoring stack

## Installation Steps

### 1. Add Helm Repositories

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

### 2. Create Namespace

```bash
kubectl create namespace monitoring
```

### 3. Install kube-prometheus-stack

This installs Prometheus, Grafana, AlertManager, and various exporters:

```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values kube-prometheus-stack-values.yaml \
  --wait \
  --timeout 10m
```

### 4. Install Loki

Deploy Loki for log aggregation:

```bash
helm install loki grafana/loki \
  --namespace monitoring \
  --values loki-values.yaml \
  --wait \
  --timeout 10m
```

### 5. Install Grafana Alloy

Deploy Alloy as the unified collection agent:

```bash
helm install alloy grafana/alloy \
  --namespace monitoring \
  --values alloy-values.yaml \
  --wait \
  --timeout 5m
```

## Verification

### Check Pod Status

All pods should be running:

```bash
kubectl get pods -n monitoring
```

Expected pods:
- `kube-prometheus-stack-prometheus-*` (1 pod)
- `kube-prometheus-stack-grafana-*` (1 pod)
- `kube-prometheus-stack-operator-*` (1 pod)
- `kube-prometheus-stack-alertmanager-*` (1 pod)
- `kube-prometheus-stack-kube-state-metrics-*` (1 pod)
- `prometheus-node-exporter-*` (1 per node)
- `loki-*` (1 pod)
- `alloy-*` (1 per node)

### Check Services

```bash
kubectl get svc -n monitoring
```

### Check Persistent Volumes

```bash
kubectl get pvc -n monitoring
```

## Access Information

### Grafana

Get the LoadBalancer IP:

```bash
kubectl get svc kube-prometheus-stack-grafana -n monitoring
```

Default credentials:
- Username: `admin`
- Password: Get the auto-generated password:
  ```bash
  kubectl get secret kube-prometheus-stack-grafana -n monitoring \
    -o jsonpath="{.data.admin-password}" | base64 --decode
  ```

### Prometheus

Access via port-forward:

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090
```

Then visit: http://localhost:9090

### AlertManager

Access via port-forward:

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-alertmanager 9093:9093
```

Then visit: http://localhost:9093

## Pre-configured Components

### Data Sources in Grafana

- **Prometheus**: Default metrics data source
- **Loki**: Log aggregation with label correlation
- **AlertManager**: For alert visualization

### Pre-installed Dashboards

- Kubernetes Cluster Overview (ID: 7249)
- Kubernetes Nodes (ID: 15520)
- Kubernetes Resources (ID: 13332)
- Talos Linux (ID: 19122)
- Loki Dashboard (auto-installed with self-monitoring)

### Metrics Collection

Alloy collects:
- Node metrics (CPU, memory, disk, network)
- Container metrics (cAdvisor)
- Kubernetes metrics (API server, etcd, scheduler, controller-manager)
- Pod metrics (with Prometheus annotations)
- Talos-specific metrics

### Log Collection

Alloy collects:
- All pod logs from all namespaces
- System logs (if accessible)
- Automatic parsing of JSON logs
- Label extraction for filtering

## Resource Usage

### Expected Resource Consumption

- **Prometheus**: 2-4GB RAM, 50GB disk
- **Loki**: 0.5-2GB RAM, 30GB disk
- **Grafana**: 256-512MB RAM, 10GB disk
- **Alloy**: 256-512MB RAM per node
- **Other components**: ~1GB RAM total
- **Total**: ~6-8GB RAM, ~92GB disk

### Retention Policies

- **Prometheus**: 15 days metrics retention
- **Loki**: 7 days log retention
- **AlertManager**: 2GB storage for alerts

## Upgrade Commands

### Update Helm Repositories

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

# Alloy
helm upgrade alloy grafana/alloy \
  --namespace monitoring \
  --values alloy-values.yaml
```

## Uninstall (if needed)

```bash
# Remove Helm releases
helm uninstall alloy -n monitoring
helm uninstall loki -n monitoring
helm uninstall kube-prometheus-stack -n monitoring

# Clean up PVCs (data will be lost!)
kubectl delete pvc -n monitoring --all

# Remove namespace
kubectl delete namespace monitoring
```

## Troubleshooting

### Pods not starting

Check pod logs:
```bash
kubectl logs -n monitoring <pod-name>
```

### High memory usage

Reduce retention or adjust resource limits in values files.

### Grafana not accessible

Check LoadBalancer status:
```bash
kubectl describe svc kube-prometheus-stack-grafana -n monitoring
```

### Missing metrics

Verify Alloy is running on all nodes:
```bash
kubectl get pods -n monitoring -l app.kubernetes.io/name=alloy
```

## Next Steps

1. **Configure Alerts**: Add custom PrometheusRule resources
2. **Add Dashboards**: Import community dashboards from grafana.com
3. **Set up Notifications**: Configure AlertManager receivers
4. **Monitor Applications**: Add Prometheus annotations to your pods

## Notes for ArgoCD Integration

Once the stack is tested and working, it can be managed by ArgoCD. The values files are already configured for GitOps deployment.
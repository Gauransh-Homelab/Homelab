# Monitoring Stack Configuration Guide

This document explains the custom values and configurations used in the LGTM (Loki, Grafana, Tempo, Metrics) monitoring stack deployment for homelab environments.

## Overview

The monitoring stack consists of three main components:
- **kube-prometheus-stack**: Provides Prometheus, Grafana, and Alertmanager
- **Loki**: Centralized log aggregation and querying
- **Tempo**: Distributed tracing backend

## Resource Optimization for Homelab

### CPU and Memory Limits
All components have been optimized for homelab environments with limited resources (4c/8GB + 4c/16GB cluster):

**Prometheus**: 
- CPU: 1000m limit, 200m request (reduced from 2000m/500m)
- Memory: 2Gi limit, 1Gi request (reduced from 4Gi/2Gi)

**Grafana**:
- CPU: 200m limit, 50m request (reduced from 500m/100m) 
- Memory: 512Mi limit, 256Mi request (reduced from 1Gi/512Mi)

**Supporting Components** (nodeExporter, kubeStateMetrics, etc.):
- Request values reduced by 50% while maintaining same limits
- Example: CPU requests changed from 50m to 25m

### Storage Configuration
All persistent storage uses `synology-iscsi` storage class for consistency:

**Prometheus**: 30Gi (reduced from 50Gi) with 15-day retention
**Grafana**: 5Gi (reduced from 10Gi) for dashboards and settings
**Loki**: 20Gi main storage + 5Gi each for write/read/backend (reduced from 50Gi/10Gi)
**Tempo**: 10Gi (reduced from 20Gi) with 3-day trace retention

## LGTM Stack Integration

### Data Source Auto-Configuration
Grafana is pre-configured with data sources for seamless integration:

```yaml
datasources:
  - Prometheus: Default metrics source (http://kube-prometheus-stack-prometheus:9090)
  - Loki: Log aggregation (http://loki:3100) with trace correlation
  - Tempo: Distributed tracing (http://tempo:3100) with log correlation
```

### Cross-Component Correlation
- **Logs to Traces**: Loki configured to extract traceIDs and link to Tempo
- **Traces to Logs**: Tempo configured to filter logs by trace/span IDs
- **Metrics to Everything**: Prometheus scrapes metrics from all components

### Service Discovery
Prometheus automatically discovers and scrapes:
- Loki metrics endpoint (job: 'loki')
- Tempo metrics endpoint (job: 'tempo')
- All Kubernetes services with proper annotations

## Performance Tuning

### Scraping and Monitoring Intervals
All serviceMonitor intervals set to 60s (increased from 30s) to reduce CPU load:
- Reduces Prometheus scraping frequency
- Lowers overall cluster resource consumption
- Maintains adequate monitoring granularity for homelab use

### Query Optimization
**Loki Query Limits**:
- `max_query_parallelism`: 8 (reduced from 16) to limit concurrent queries
- `ingestion_rate_mb`: 32 (reduced from 64) to control log ingestion rate
- `ingestion_burst_size_mb`: 64 (reduced from 128) for burst control

**Structured Metadata**:
```yaml
structured_metadata:
  enabled: true
  max_entries_per_log: 128
```
Enables JSON log parsing and structured field extraction for better query performance.

## Data Retention Policies

### Log Retention (Loki)
- **Retention Period**: 168h (7 days) for log data
- **Compaction**: 10-minute intervals for storage optimization
- **Deletion Delay**: 2h before permanent removal

### Trace Retention (Tempo)
- **Block Retention**: 72h (3 days, reduced from 7 days)
- **Compaction Window**: 1h for efficient storage
- **WAL Path**: `/var/tempo/wal` for write-ahead logging

### Metrics Retention (Prometheus)
- **Retention Time**: 15 days for time-series data
- **Retention Size**: 45GB maximum storage usage
- **Single Replica**: Optimized for homelab (can be scaled up)

## Security Configuration

### Authentication
- **Grafana Admin**: Secure password (`homelab-secure-2024!`) replaces default
- **Loki Auth**: Disabled (`auth_enabled: false`) for simplified homelab setup
- **Tempo**: Multi-tenancy disabled for single-user environment

### Network Access
- **Grafana**: LoadBalancer service with MetalLB for external access
- **Internal Services**: ClusterIP for inter-component communication
- **Prometheus**: Internal access only, proxied through Grafana

## Multi-Format Trace Ingestion (Tempo)

Tempo is configured to accept traces in multiple formats:
- **OpenTelemetry**: gRPC (4317) and HTTP (4318)
- **Jaeger**: Thrift compact (6831), binary (6832), gRPC (14250), HTTP (14268)  
- **Zipkin**: HTTP (9411)
- **OpenCensus**: gRPC (55678)

This allows applications using different tracing libraries to send data to the same backend.

## Dashboard Integration

### Pre-configured Dashboards
Grafana includes community dashboards for immediate visibility:
- **Kubernetes Cluster**: Overall cluster health (ID: 7249)
- **Node Exporter**: Host metrics monitoring (ID: 1860) 
- **Loki**: Log analysis dashboard (ID: 13639)
- **Tempo**: Trace analysis dashboard (ID: 16698)

### Service Monitors
All components expose Prometheus metrics with proper labeling:
- `release: kube-prometheus-stack` for automatic discovery
- Consistent scraping configuration across the stack
- Built-in alerting rules for component health

## Deployment Modes

### Single Binary Deployments
Both Loki and Tempo run in single binary mode for homelab simplicity:
- **Loki**: All components (distributor, ingester, querier) in one process
- **Tempo**: Simplified deployment without separate microservices
- **Filesystem Backend**: Local storage instead of object storage (S3, etc.)

This reduces complexity and resource overhead while maintaining full functionality for homelab scale.
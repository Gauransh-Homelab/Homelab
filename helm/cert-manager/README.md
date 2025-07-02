# Cert-Manager Configuration

This directory contains the cert-manager setup for automatic certificate management with Traefik.

## Overview

Cert-manager has been installed in the `traefik` namespace and configured to use the existing DNS secrets for automatic certificate provisioning via Let's Encrypt.

## Files

- `values.yaml` - Helm values for cert-manager installation
- `cloudflare-issuer.yaml` - Production ClusterIssuer for Cloudflare domains
- `cloudflare-staging-issuer.yaml` - Staging ClusterIssuer for testing
- `duckdns-issuer.yaml` - ClusterIssuer for DuckDNS domains (requires webhook)

## Installed ClusterIssuers

### Production
- `letsencrypt-cloudflare` - For Cloudflare-managed domains
- `letsencrypt-cloudflare-staging` - For testing with Cloudflare domains

### DuckDNS (Requires Webhook)
- `letsencrypt-duckdns` - For DuckDNS domains (webhook not yet installed)

## Usage with Traefik IngressRoute

To automatically generate certificates, add annotations to your IngressRoute:

```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: my-app
  annotations:
    # For production certificates
    cert-manager.io/cluster-issuer: "letsencrypt-cloudflare"
    # For staging certificates (use for testing)
    # cert-manager.io/cluster-issuer: "letsencrypt-cloudflare-staging"
spec:
  entryPoints:
    - websecure
  routes:
  - match: Host(`example.com`)
    kind: Rule
    services:
    - name: my-app-service
      port: 80
  tls:
    secretName: example-com-tls  # cert-manager will create this secret
```

## Manual Certificate Creation

You can also create certificates manually:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com-tls
  namespace: traefik
spec:
  secretName: example-com-tls
  issuerRef:
    name: letsencrypt-cloudflare
    kind: ClusterIssuer
  dnsNames:
  - example.com
  - www.example.com
```

## DNS Secrets

The following secrets are used by the ClusterIssuers:

- `dns-secrets` in `traefik` namespace
  - `cloudflare-token` - Cloudflare API token
  - `duckdns-token` - DuckDNS token

## Installation Commands

```bash
# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace traefik \
  --values values.yaml

# Apply ClusterIssuers
kubectl apply -f cloudflare-issuer.yaml
kubectl apply -f cloudflare-staging-issuer.yaml
```

## Verification

Check ClusterIssuer status:
```bash
kubectl get clusterissuers
kubectl describe clusterissuer letsencrypt-cloudflare
```

Check certificates:
```bash
kubectl get certificates -n traefik
kubectl describe certificate my-cert -n traefik
```

## DuckDNS Setup

To use DuckDNS certificates, you need to install a webhook:

```bash
# Add webhook repository (example)
helm repo add cert-manager-webhook-duckdns https://ebrianne.github.io/helm-charts
helm install cert-manager-webhook-duckdns cert-manager-webhook-duckdns/cert-manager-webhook-duckdns \
  --namespace traefik

# Then apply the DuckDNS issuer
kubectl apply -f duckdns-issuer.yaml
```

## Benefits

- ✅ No persistent storage needed for certificates
- ✅ Automatic certificate renewal
- ✅ Kubernetes-native certificate management
- ✅ Better monitoring and observability
- ✅ Integration with existing DNS secrets
- ✅ Works with existing Traefik LoadBalancer configuration
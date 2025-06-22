# Traefik Helm Chart Installation - Nginx Proxy Manager Replacement

This setup provides all the functionality of Nginx Proxy Manager with better Kubernetes integration:
- ✅ Automatic SSL certificates via Let's Encrypt
- ✅ Support for multiple DNS providers (DuckDNS + Cloudflare)
- ✅ Web dashboard for management
- ✅ High availability with 2 replicas
- ✅ LoadBalancer integration with MetalLB

## Prerequisites

1. **Update DNS API Tokens** in `dns-secrets.yaml`:
   - Replace `REPLACE_WITH_YOUR_DUCKDNS_TOKEN` with your DuckDNS token
   - Replace `REPLACE_WITH_YOUR_CLOUDFLARE_API_TOKEN` with your Cloudflare API token

2. **Update Email Address** in `values.yaml`:
   - Change `your-email@example.com` to your actual email (required for Let's Encrypt)

3. **Update Dashboard Domain** in `dashboard-route.yaml`:
   - Choose either Cloudflare or DuckDNS route (delete the other)
   - Update the Host() domain to your actual domain

4. **Generate Dashboard Password** (optional, default is admin/admin):
   - Use: `htpasswd -nb admin yourpassword`
   - Update the hash in `dashboard-secret.yaml`

## Installation Steps

```bash
# 1. Create namespace
kubectl create namespace traefik

# 2. Add Helm repository
helm repo add traefik https://traefik.github.io/charts
helm repo update

# 3. Install Traefik CRDs first
helm install traefik-crds traefik/traefik-crds -n traefik

# 4. Create DNS secrets (update tokens first!)
kubectl apply -f dns-secrets.yaml

# 5. Install Traefik with custom values
helm install traefik traefik/traefik -n traefik -f values.yaml

# 6. Apply security and dashboard configuration
kubectl apply -f dashboard-secret.yaml
kubectl apply -f middlewares.yaml
kubectl apply -f dashboard-route.yaml
kubectl apply -f ingressclass.yaml
```

## Verification

```bash
# Check Traefik pods are running
kubectl get pods -n traefik

# Check LoadBalancer service got external IP
kubectl get svc -n traefik

# Check dashboard access (update domain)
curl -k https://traefik.yourdomain.com
```

## Dashboard Access

- **URL**: `https://traefik.yourdomain.com` (update with your domain)
- **Username**: `admin`
- **Password**: `admin` (change this in dashboard-secret.yaml)

## Adding New Services

### Example: Route DuckDNS domain to a service

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: my-app
  namespace: default
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`myapp.myusername.duckdns.org`)
      kind: Rule
      services:
        - name: my-app-service
          port: 80
      middlewares:
        - name: security-headers@kubernetescrd
  tls:
    certResolver: duckdns  # Automatic SSL from DuckDNS
```

### Example: Route Cloudflare domain to a service

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: my-app-cf
  namespace: default
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`myapp.mydomain.com`)
      kind: Rule
      services:
        - name: my-app-service
          port: 80
      middlewares:
        - name: security-headers@kubernetescrd
  tls:
    certResolver: cloudflare  # Automatic SSL from Cloudflare
```

## Troubleshooting

### Check certificate status
```bash
kubectl get certificate -n traefik
kubectl describe certificate -n traefik
```

### Check Traefik logs
```bash
kubectl logs -n traefik deployment/traefik -f
```

### Common Issues

1. **DNS tokens not working**: Verify tokens have correct permissions
2. **Certificates not issued**: Check DNS propagation and email address
3. **Dashboard not accessible**: Verify domain points to LoadBalancer IP
4. **502 errors**: Check service names and ports in IngressRoute

## Upgrades

```bash
# Update Helm repo
helm repo update

# Upgrade CRDs first
helm upgrade traefik-crds traefik/traefik-crds -n traefik

# Upgrade Traefik
helm upgrade traefik traefik/traefik -n traefik -f values.yaml
```

## Security Notes

- Dashboard is protected with BasicAuth
- All HTTP traffic redirects to HTTPS
- Security headers are applied to all routes
- Rate limiting middleware available
- IP whitelisting middleware available for sensitive services
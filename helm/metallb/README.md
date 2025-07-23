# MetalLB Configuration

## Installation Steps

1. Install MetalLB via Helm:
```bash
helm install metallb metallb/metallb --namespace metallb --create-namespace
```

2. **IMPORTANT**: Apply the configuration after installation:
```bash
kubectl apply -f metallb-config.yaml
```

## Configuration

The `metallb-config.yaml` file contains:
- **IPAddressPool**: Defines the IP range (192.168.10.10-192.168.10.40)
- **L2Advertisement**: Enables Layer 2 (ARP) announcements for the IPs

Both resources are required for MetalLB to function properly in Layer 2 mode.

## Troubleshooting

If LoadBalancer services show `<pending>` for EXTERNAL-IP:
1. Check if IPAddressPool exists: `kubectl get ipaddresspools -n metallb`
2. Check if L2Advertisement exists: `kubectl get l2advertisements -n metallb`
3. Check MetalLB speaker logs: `kubectl logs -n metallb -l app.kubernetes.io/component=speaker`
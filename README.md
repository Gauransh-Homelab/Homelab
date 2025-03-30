# 🏠 Homelab Setup

<div align="center">

![Homelab Status](https://img.shields.io/badge/status-operational-brightgreen)
![Proxmox](https://img.shields.io/badge/Proxmox-8.0-orange)
![Services](https://img.shields.io/badge/Services-10+-blue)
![Last Updated](https://img.shields.io/badge/Last%20Updated-March%202025-lightgrey)

*A personal homelab environment with virtualization, media services, and remote access*

[Hardware](#-hardware) • [Network](#-network) • [Services](#-services) • [Future Plans](#-future-plans)

</div>

---

## 🔍 Quick Overview

> **What**: Home server setup for media, development, and learning  
> **Why**: Self-host services with full control and customization  
> **How**: Proxmox VE + Docker + LXC Containers  

---

## 💻 Hardware

<table>
  <tr>
    <th width="40%">Component</th>
    <th width="60%">Details</th>
  </tr>
  <tr>
    <td><strong>Main Server</strong><br/><i>Acer XC-780</i></td>
    <td>
      • Intel i5-7400<br/>
      • 16GB DDR4 RAM<br/>
      • NVIDIA GT-730
    </td>
  </tr>
  <tr>
    <td><strong>Storage</strong><br/><i>Synology DS423+</i></td>
    <td>
      • 2x 12TB drives in SHR<br/>
      • 1-drive fault tolerance<br/>
      • Dual Ethernet connectivity
    </td>
  </tr>
</table>

---

## 🌐 Network

```mermaid
graph TD
    Internet((Internet)) --> Router
    Router --> Switch[TP-Link 8-Port Switch]
    Switch --> Server[Acer XC-780]
    Switch --> NAS[Synology DS423+]
    Switch --> OtherDevices[Other Devices]
    
    class Server,NAS emphasis
```

> **Switch**: TP-Link 8-Port Unmanaged Gigabit Switch  
> **Connectivity**: All Ethernet (1Gbps)  
> **NAS Feature**: Link aggregation with dual Ethernet ports  

---

## 🧩 Software Architecture

<table>
  <tr>
    <th>Layer</th>
    <th>Component</th>
    <th>Purpose</th>
  </tr>
  <tr>
    <td rowspan="2"><strong>Base</strong></td>
    <td>Proxmox VE</td>
    <td>Hypervisor for VMs & LXC management</td>
  </tr>
  <tr>
    <td>Tailscale</td>
    <td>Secure remote access (exit node)</td>
  </tr>
  <tr>
    <td rowspan="2"><strong>Network</strong></td>
    <td>Nginx Proxy Manager</td>
    <td>Reverse proxy for service access</td>
  </tr>
  <tr>
    <td>DuckDNS</td>
    <td>Dynamic DNS for domain management</td>
  </tr>
</table>

---

## 🚀 Services

### Development Tools
- ⌨️ **Wastebin** - Code snippet sharing (LXC container)

### Media Stack
<div align="center">

| Service | Type | Function | Container |
|---------|------|----------|-----------|
| **Jellyfin** | 📺 Media | Streaming server | Docker |
| **Jellyseerr** | 🔍 Frontend | Media requests | Docker |
| **Radarr** | 🎬 Manager | Movies | Docker |
| **Sonarr** | 📺 Manager | TV Shows | Docker |
| **Prowlarr** | 🔍 Indexer | Content search | Docker |
| **Bazarr** | 💬 Subtitles | Subtitle management | Docker |
| **qBittorrent** | ⬇️ Downloader | Torrent client | Docker |
| **NZBGet** | ⬇️ Downloader | Usenet client | Docker |
| **Glueton** | 🔒 VPN | ExpressVPN binding | Docker |
| **Notifiarr** | 🔔 Notifications | Discord alerts | Docker |

</div>

> 💡 **Note**: All media services managed via Portainer in a dedicated LXC container
>
> ⚠️ **Current Issue**: Tdarr disabled due to GPU compatibility with Intel Arc A310

### Quality Setup
Sonarr and Radarr follow [TRaSH guides](https://trash-guides.info/) for optimal quality profiles.

---

## 🗄️ Storage Architecture

```
Synology DS423+ (24TB Raw / ~12TB Usable)
├── Media
│   ├── Movies
│   ├── TV
│   └── Music
├── Backups
│   └── VM Backups
└── Personal
    └── Documents
```

---

## 🔮 Future Plans

<div align="center">

### Current vs Future Architecture

| Component | Current | Planned |
|-----------|---------|---------|
| **Virtualization** | Proxmox VE | Talos Linux + K8s |
| **Container Mgmt** | Docker/Portainer | Kubernetes |
| **Cloud Integration** | None | Digital Ocean K8s |
| **GPU Access** | Disabled | Direct K8s passthrough |
| **Storage** | Direct mount | iSCSI for K8s |

</div>

### Migration Path
1. Set up Digital Ocean Kubernetes cluster
2. Migrate Docker containers to cloud K8s
3. Replace Proxmox with Talos Linux locally
4. Configure GPU passthrough
5. Implement iSCSI storage

> 🚧 **TODO**: Create detailed migration plan document with timeline

---

<div align="center">

## 🤝 Contributing

This is a personal project, but suggestions welcome via issues!

## 📜 License

[MIT License](LICENSE)

</div>


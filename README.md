# ansible-role-headscale

Ansible role to deploy [Headscale](https://github.com/juanfont/headscale) via Docker with Traefik reverse proxy integration.

## Requirements

- Docker installed and running on the target host
- Traefik configured as reverse proxy
- `community.docker` Ansible collection

## Dependencies

- `mikinhas.docker`
- `mikinhas.traefik`

## Role Variables

### General

| Variable | Default | Description |
|---|---|---|
| `headscale_version` | `0.28.0` | Headscale Docker image tag |
| `headscale_domain` | `headscale.example.com` | Public domain for the Headscale server |
| `headscale_data_dir` | `/opt/headscale` | Data directory on the host |
| `headscale_config_dir` | `{{ headscale_data_dir }}/config` | Configuration directory on the host |
| `headscale_container_name` | `headscale` | Docker container name |
| `headscale_image` | `headscale/headscale:{{ headscale_version }}` | Full Docker image reference |
| `headscale_docker_network` | `headscale` | Docker network to attach the container to |

### Server

| Variable | Default | Description |
|---|---|---|
| `headscale_listen_addr` | `0.0.0.0:8080` | HTTP listen address |
| `headscale_metrics_listen_addr` | `0.0.0.0:9090` | Metrics endpoint listen address |
| `headscale_grpc_listen_addr` | `0.0.0.0:50443` | gRPC listen address |

### Database

| Variable | Default | Description |
|---|---|---|
| `headscale_database_type` | `sqlite` | Database type |
| `headscale_database_path` | `/var/lib/headscale/db.sqlite` | Path to the SQLite database (inside the container) |

### DERP

| Variable | Default | Description |
|---|---|---|
| `headscale_derp_urls` | `["https://controlplane.tailscale.com/derpmap/default"]` | DERP map URLs |
| `headscale_derp_auto_update` | `true` | Enable automatic DERP map updates |
| `headscale_derp_update_frequency` | `24h` | DERP map update frequency |

### DNS

| Variable | Default | Description |
|---|---|---|
| `headscale_dns_base_domain` | `tailnet.local` | Base domain for MagicDNS |
| `headscale_dns_magic_dns` | `true` | Enable MagicDNS |
| `headscale_dns_nameservers_global` | `["1.1.1.1", "9.9.9.9"]` | Global DNS nameservers |

### IP Prefixes

| Variable | Default | Description |
|---|---|---|
| `headscale_prefixes_v4` | `100.64.0.0/10` | IPv4 prefix for the tailnet |

### Exit Node

| Variable | Default | Description |
|---|---|---|
| `headscale_exit_node` | `false` | Enable Tailscale exit node |
| `headscale_exit_node_container_name` | `tailscale-exit-node` | Exit node Docker container name |
| `headscale_exit_node_image` | `tailscale/tailscale:v1.96.3` | Exit node Docker image |
| `headscale_exit_node_user` | `exit-node` | Headscale user for the exit node |
| `headscale_exit_node_hostname` | `exit-node` | Hostname of the exit node in the tailnet |
| `headscale_exit_node_state_dir` | `{{ headscale_data_dir }}/tailscale-exit-node` | State directory for the exit node |

### Traefik

| Variable | Default | Description |
|---|---|---|
| `headscale_traefik_entrypoint` | `websecure` | Traefik entrypoint |
| `headscale_traefik_tls_certresolver` | `letsencrypt` | Traefik TLS certificate resolver |
| `headscale_traefik_labels` | `{}` | Additional Traefik labels to merge with defaults |

## Example Playbook

```yaml
- hosts: headscale
  roles:
    - role: mikinhas.headscale
      vars:
        headscale_version: "0.28.0"
        headscale_domain: "hs.example.com"
```

## License

MIT

## Author

Michael MACHADO

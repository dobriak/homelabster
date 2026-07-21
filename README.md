# Homelabster

A local-first FastAPI dashboard for YAML-defined homelab services. It groups service tiles into configurable categories, checks service health, and serves Bootstrap and htmx from local static files. Font Awesome Free is loaded for category icons.

## Features

- Create, edit, delete, and organize service tiles by category.
- Create, edit, and delete IPAM entries (CIDR ranges, hosts with IP addresses, and named ports) on the dedicated **IPAM** page. You can manage multiple unrelated CIDRs.
- When creating or editing a service, click **Browse** next to the fallback or health URL fields to pick an `IP:port` pair from your IPAM data instead of typing it manually.
- Configure category names, Font Awesome icons, and dashboard order. The fixed **All** category contains unassigned services.
- Open each service through its FQDN or compact `ip` fallback link.
- Optionally poll a health URL and display the current health state.
- Preview a matching Dashboard Icons catalog icon while editing a service, or upload an SVG, PNG, or WEBP icon to override it.

## Setup and run

Install the Python dependencies, then create your private runtime configuration from the sanitized sample:

```sh
uv sync --group dev
cp config/services.yaml.example config/services.yaml
cp config/categories.yaml.example config/categories.yaml
uv run fastapi dev src/homelabster/main.py
```

Open `http://127.0.0.1:8000`.

## Docker

Start the dashboard with Docker Compose:

```sh
docker compose up --build -d
```

Open `http://127.0.0.1:8000`. The first startup creates `config/services.yaml` and
`config/categories.yaml` from their example files. The Compose file bind-mounts
`./config` into the container, so configuration changes and uploaded icons persist
on the host. Stop it with `docker compose down`.

## Using the dashboard

- Use **IPAM** to manage CIDR ranges, hosts, IPs, and named ports. When creating or editing a service, the **Browse** button next to the fallback and health URL fields lets you pick an `IP:port` pair from your IPAM data.
- Use **Settings** to set the dashboard title, UI theme, health-check interval, categories, and category order.
- Use **Services** to create, edit, delete, and categorize homelab services. A service can be left unassigned to appear in **All**.
- When creating or editing a service, the icon preview uses the service name by default. Enter an optional **Icon lookup name**—for example, `Proxmox` for a tile named `Arbitrary String`—to use that catalog match instead. Uploading a custom icon always takes precedence.
- Click a service name to open its FQDN; use its `ip` button for the IP:port fallback.

## Runtime data and backups

`config/services.yaml`, `config/categories.yaml`, `config/ipam.yaml`, and downloaded icon files in `config/icons/` are deliberately ignored by Git: they can contain private hostnames, IP addresses, and locally cached assets. The versioned configuration templates are [services.yaml.example](config/services.yaml.example) and [categories.yaml.example](config/categories.yaml.example).

Back up `config/services.yaml`, `config/categories.yaml`, `config/ipam.yaml`, and `config/icons/` if you want to preserve your configuration and custom or downloaded icons.

To store runtime data outside the repository, set `HOMELABSTER_DATA_DIR` before starting the app. In that case, copy the example files to `$HOMELABSTER_DATA_DIR`; `ipam.yaml` is created automatically on first use, and downloaded icons are stored beside them in `$HOMELABSTER_DATA_DIR/icons/`.

## Tests

```sh
uv run pytest
```

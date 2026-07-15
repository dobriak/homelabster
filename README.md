# Homelabster

A FastAPI dashboard for YAML-defined homelab services. It serves Bootstrap and htmx from local static files; Font Awesome Free is loaded for configurable category icons.

## Setup and run

Install the Python dependencies, then create your private runtime configuration from the sanitized sample:

```sh
uv sync --group dev
cp config/services.yaml.example config/services.yaml
cp config/categories.yaml.example config/categories.yaml
uv run fastapi dev src/homelabster/main.py
```

Open `http://127.0.0.1:8000`.

## Using the dashboard

- Use **Settings** to set the dashboard title, UI theme, health-check interval, service categories, and category order. The fixed **All** category holds unassigned services.
- Use **Services** to create, edit, delete, and categorize homelab services.
- Click a service name to open its FQDN; use its `ip` button for the IP:port fallback.

## Runtime data and backups

`config/services.yaml`, `config/categories.yaml`, and downloaded icon files in `config/icons/` are deliberately ignored by Git: they can contain private hostnames, IP addresses, and locally cached assets. The versioned configuration templates are [services.yaml.example](config/services.yaml.example) and [categories.yaml.example](config/categories.yaml.example).

Back up `config/services.yaml`, `config/categories.yaml`, and `config/icons/` if you want to preserve your configuration and custom or downloaded icons.

To store runtime data outside the repository, set `HOMELABSTER_DATA_DIR` before starting the app. In that case, copy both example files to `$HOMELABSTER_DATA_DIR`; downloaded icons are stored beside them in `$HOMELABSTER_DATA_DIR/icons/`.

## Tests

```sh
uv run pytest
```

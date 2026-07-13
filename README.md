# Homelabster

A local-only FastAPI dashboard for YAML-defined homelab services. It serves Bootstrap and htmx from local static files, so the dashboard does not need browser CDN access after installation.

## Setup and run

Install the Python dependencies, then create your private runtime configuration from the sanitized sample:

```sh
uv sync --group dev
cp config/services.yaml.example config/services.yaml
uv run fastapi dev src/homelabster/main.py
```

Open `http://127.0.0.1:8000`.

## Using the dashboard

- Use **Settings** to set the dashboard title, UI theme, and health-check interval.
- Use **Services** to create, edit, and delete homelab services.
- Click a service name to open its FQDN; use its `ip` button for the IP:port fallback.

## Runtime data and backups

`config/services.yaml` and downloaded icon files in `config/icons/` are deliberately ignored by Git: they can contain private hostnames, IP addresses, and locally cached assets. The only versioned configuration file is [config/services.yaml.example](config/services.yaml.example).

Back up both `config/services.yaml` and `config/icons/` if you want to preserve your configuration and custom or downloaded icons.

To store runtime data outside the repository, set `HOMELABSTER_DATA_DIR` before starting the app. In that case, copy the example file to `$HOMELABSTER_DATA_DIR/services.yaml` first; downloaded icons are stored beside it in `$HOMELABSTER_DATA_DIR/icons/`.

## Tests

```sh
uv run pytest
```

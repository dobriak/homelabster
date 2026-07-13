from pathlib import Path

from fastapi.testclient import TestClient

from homelabster.main import create_app


def client(tmp_path: Path) -> TestClient:
    config = tmp_path / "services.yaml"
    config.write_text("version: 1\nservices: []\n")
    app = create_app(config)
    app.state.icons._metadata = {}
    return TestClient(app)


def test_dashboard_and_htmx_grid(tmp_path: Path):
    with client(tmp_path) as test_client:
        response = test_client.get("/")
        assert response.status_code == 200
        assert 'hx-trigger="load, every 30s"' in response.text
        response = test_client.get("/partials/services")
        assert "No services configured" in response.text


def test_admin_settings_update_dashboard(tmp_path: Path):
    with client(tmp_path) as test_client:
        admin = test_client.get("/admin")
        assert admin.status_code == 200
        assert '<a class="nav-link" href="/admin">Settings</a>' in admin.text
        assert '<a class="nav-link" href="/services">Services</a>' in admin.text
        assert 'href="/">Homelabster</a>' in admin.text

        saved = test_client.post(
            "/admin/settings",
            data={"dashboard_title": "Command Center", "theme": "dark", "health_check_interval_seconds": "45"},
        )
        assert saved.status_code == 200
        assert saved.headers["HX-Refresh"] == "true"
        config = (tmp_path / "services.yaml").read_text()
        assert "dashboard_title: Command Center" in config
        assert "theme: dark" in config
        assert "health_check_interval_seconds: 45" in config

        dashboard = test_client.get("/")
        assert "Command Center" in dashboard.text
        assert 'data-bs-theme="dark"' in dashboard.text
        assert 'hx-trigger="load, every 45s"' in dashboard.text
        assert "Your homelab at a glance" not in dashboard.text


def test_services_crud_flow(tmp_path: Path):
    with client(tmp_path) as test_client:
        payload = {"name": "Grafana", "service_id": "grafana", "primary_url": "https://grafana.local", "fallback_url": "http://10.0.0.8:3000", "health_url": ""}
        assert test_client.get("/services").status_code == 200
        assert test_client.get("/admin/services").status_code == 404
        created = test_client.post("/services", data=payload)
        assert created.status_code == 200
        assert 'id="service-grafana"' in created.text
        assert "grafana" in (tmp_path / "services.yaml").read_text()

        payload["name"] = "Metrics"
        updated = test_client.put("/services/grafana", data=payload)
        assert updated.status_code == 200
        assert "Metrics" in updated.text

        deleted = test_client.delete("/services/grafana")
        assert deleted.status_code == 200
        assert "services: []" in (tmp_path / "services.yaml").read_text()


def test_service_tile_uses_title_and_compact_ip_link(tmp_path: Path):
    with client(tmp_path) as test_client:
        test_client.post(
            "/services",
            data={"name": "Grafana", "service_id": "grafana", "primary_url": "https://grafana.local", "fallback_url": "http://10.0.0.8:3000", "health_url": ""},
        )
        tile = test_client.get("/partials/services")
        assert 'href="https://grafana.local"' in tile.text
        assert '>Grafana</a></h2><a class="btn btn-sm btn-outline-secondary"' in tile.text
        assert '>ip</a>' in tile.text
        assert "Use IP:port fallback" not in tile.text
        assert ">Open Grafana</a>" not in tile.text
        assert "btn btn-primary" not in tile.text
        assert "Not checked yet" not in tile.text
        assert 'aria-label="Health status: unknown"' in tile.text


def test_services_reports_inline_validation(tmp_path: Path):
    with client(tmp_path) as test_client:
        response = test_client.post("/services", data={"name": "Bad", "primary_url": "ftp://bad", "fallback_url": "http://10.0.0.8"})
        assert response.status_code == 422
        assert "must be an absolute http or https URL" in response.text
        assert response.headers["HX-Retarget"] == "#service-form-slot"


def test_admin_rejects_invalid_settings(tmp_path: Path):
    with client(tmp_path) as test_client:
        response = test_client.post(
            "/admin/settings",
            data={"dashboard_title": "", "theme": "neon", "health_check_interval_seconds": "2"},
        )
        assert response.status_code == 422
        assert "Input should be" in response.text

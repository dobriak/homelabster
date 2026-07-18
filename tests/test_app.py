from pathlib import Path

from fastapi.testclient import TestClient

from homelabster.main import create_app
from homelabster.repository import CategoriesRepository


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
        assert 'id="service-search"' in response.text
        assert 'hx-target="#service-grid"' in response.text
        response = test_client.get("/partials/services")
        assert "No services configured" in response.text


def test_dashboard_search_filters_tiles_and_keeps_matching_categories(tmp_path: Path):
    with client(tmp_path) as test_client:
        assert test_client.post("/admin/categories", data={"name": "Infrastructure", "icon": "fas fa-server"}).status_code == 200
        assert test_client.post("/admin/categories", data={"name": "Monitoring", "icon": "fas fa-chart-line"}).status_code == 200
        for service in (
            {"name": "Proxmox", "service_id": "proxmox", "primary_url": "https://proxmox.local", "fallback_url": "http://10.0.0.2", "category": "Infrastructure"},
            {"name": "Proxifier", "service_id": "proxifier", "primary_url": "https://proxifier.local", "fallback_url": "http://10.0.0.3", "category": "Monitoring"},
            {"name": "Grafana", "service_id": "grafana", "primary_url": "https://grafana.local", "fallback_url": "http://10.0.0.4", "category": "Monitoring"},
        ):
            assert test_client.post("/services", data=service).status_code == 200

        filtered = test_client.get("/partials/services", params={"search": "PrOx"})
        assert filtered.status_code == 200
        assert "Proxmox" in filtered.text
        assert "Proxifier" in filtered.text
        assert "Grafana" not in filtered.text
        assert filtered.text.count(">Infrastructure</h2>") == 1
        assert filtered.text.count(">Monitoring</h2>") == 1

        no_matches = test_client.get("/partials/services", params={"search": "missing"})
        assert "No services match “missing”." in no_matches.text


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
        assert "Service was not saved" in response.headers["HX-Trigger"]


def test_service_forms_preview_the_default_and_current_icons(tmp_path: Path):
    with client(tmp_path) as test_client:
        new_form = test_client.get("/services/new")
        assert new_form.status_code == 200
        assert 'id="service-icon-preview"' in new_form.text
        assert "default-service.svg" in new_form.text

        test_client.post(
            "/services",
            data={"name": "Grafana", "service_id": "grafana", "primary_url": "https://grafana.local", "fallback_url": "http://10.0.0.8:3000"},
        )
        edit_form = test_client.get("/services/grafana/edit")
        assert edit_form.status_code == 200
        assert "default-service.svg" in edit_form.text

        (tmp_path / "services.yaml").write_text(
            """version: 1
services:
  - id: custom
    name: Custom
    primary_url: https://custom.local
    fallback_url: http://10.0.0.9:3000
    icon:
      local_filename: upload-custom.svg
"""
        )
        custom_edit_form = test_client.get("/services/custom/edit")
        assert "/icons/upload-custom.svg" in custom_edit_form.text


def test_service_icon_preview_and_success_status(tmp_path: Path):
    with client(tmp_path) as test_client:
        test_client.app.state.icons._metadata = {"grafana": {"base": "svg"}}
        preview = test_client.get("/services/icon-preview", params={"name": "Grafana"})
        assert preview.status_code == 200
        assert "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/grafana.svg" in preview.text

        saved = test_client.post(
            "/services",
            data={"name": "Manual", "service_id": "manual", "primary_url": "https://manual.local", "fallback_url": "http://10.0.0.9:3000"},
        )
        assert "Manual was saved." in saved.headers["HX-Trigger"]
        services = test_client.get("/services")
        assert "service-save-toast" in services.text
        assert "clearForm" in services.text


def test_icon_lookup_name_overrides_the_service_name_for_icon_assignment(tmp_path: Path, monkeypatch):
    resolved_names = []

    async def resolve(name: str):
        resolved_names.append(name)
        return "proxmox", "proxmox.svg"

    with client(tmp_path) as test_client:
        monkeypatch.setattr(test_client.app.state.icons, "resolve", resolve)
        payload = {
            "name": "Arbitrary String",
            "service_id": "arbitrary",
            "primary_url": "https://arbitrary.local",
            "fallback_url": "http://10.0.0.9:3000",
            "icon_lookup_name": "Proxmox",
        }
        assert test_client.post("/services", data=payload).status_code == 200
        assert resolved_names == ["Proxmox"]

        payload["icon_lookup_name"] = "Grafana"
        assert test_client.put("/services/arbitrary", data=payload).status_code == 200
        assert resolved_names == ["Proxmox", "Grafana"]

        payload.update({"name": "Custom", "service_id": "custom", "icon_lookup_name": "Proxmox"})
        assert test_client.post(
            "/services",
            data=payload,
            files={"icon_upload": ("custom.svg", b"<svg></svg>", "image/svg+xml")},
        ).status_code == 200
        assert resolved_names == ["Proxmox", "Grafana"]


def test_admin_rejects_invalid_settings(tmp_path: Path):
    with client(tmp_path) as test_client:
        response = test_client.post(
            "/admin/settings",
            data={"dashboard_title": "", "theme": "neon", "health_check_interval_seconds": "2"},
        )
        assert response.status_code == 422
        assert "Input should be" in response.text


def test_categories_crud_assignments_and_dashboard_grouping(tmp_path: Path):
    with client(tmp_path) as test_client:
        admin = test_client.get("/admin")
        assert admin.status_code == 200
        assert "Service assignments" in admin.text
        categories_path = tmp_path / "categories.yaml"
        assert "name: All" in categories_path.read_text()

        created = test_client.post("/admin/categories", data={"name": "Infrastructure", "icon": "fas fa-server"})
        assert created.status_code == 200
        assert created.headers["HX-Refresh"] == "true"
        assert "name: Infrastructure" in categories_path.read_text()
        assert "display_order: 1" in categories_path.read_text()

        assert test_client.post("/admin/categories", data={"name": "Applications", "icon": "fas fa-cubes"}).status_code == 200
        reordered = test_client.post(
            "/admin/categories/order",
            data={"category_name": ["Applications", "Infrastructure"], "display_order": ["1", "2"]},
        )
        assert reordered.status_code == 200
        assert reordered.headers["HX-Refresh"] == "true"
        category_repo = CategoriesRepository(categories_path)
        assert category_repo.get("Applications").display_order == 1
        assert category_repo.get("Infrastructure").display_order == 2

        service = {
            "name": "Grafana",
            "service_id": "grafana",
            "primary_url": "https://grafana.local",
            "fallback_url": "http://10.0.0.8:3000",
            "health_url": "",
            "category": "Infrastructure",
        }
        assert test_client.post("/services", data=service).status_code == 200
        assert "category: Infrastructure" in (tmp_path / "services.yaml").read_text()

        grid = test_client.get("/partials/services")
        assert "Infrastructure" in grid.text
        assert "fas fa-server" in grid.text
        assert "unassigned services" not in grid.text

        service.update(name="Unassigned", service_id="unassigned", category="")
        assert test_client.post("/services", data=service).status_code == 200
        grid = test_client.get("/partials/services")
        assert grid.text.index("All") < grid.text.index("Infrastructure")

        saved = test_client.post(
            "/admin/service-categories",
            data={"service_id": ["grafana", "unassigned"], "category": ["", "Infrastructure"]},
        )
        assert saved.status_code == 200
        assert saved.headers["HX-Refresh"] == "true"
        assert "category: Infrastructure" in (tmp_path / "services.yaml").read_text()

        deleted = test_client.delete("/admin/categories/Infrastructure")
        assert deleted.status_code == 200
        assert "category:" not in (tmp_path / "services.yaml").read_text()
        assert "Infrastructure" not in categories_path.read_text()

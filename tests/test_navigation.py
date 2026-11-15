from pathlib import Path

from fastapi.testclient import TestClient

from homelabster.main import create_app


def test_navigation_uses_application_icon_and_favicon(tmp_path: Path):
    config = tmp_path / "services.yaml"
    config.write_text("version: 1\nservices: []\n")
    app = create_app(config)
    app.state.icons._metadata = {}

    with TestClient(app) as test_client:
        response = test_client.get("/")

        assert response.status_code == 200
        assert 'rel="icon" href="/static/favicon.ico"' in response.text
        assert 'class="navbar-logo" src="/static/homelabster-icon.svg"' in response.text
        assert 'class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main-navigation"' in response.text
        assert 'class="collapse navbar-collapse" id="main-navigation"' in response.text
        assert 'navbar-actions d-flex align-items-center gap-3 ms-auto navbar-actions-with-search' in response.text
        assert 'class="link-mode-toggle btn-group btn-group-sm" role="group" aria-label="Service link destination"' in response.text
        assert 'class="btn btn-outline-secondary" data-service-link-mode="fqdn" aria-pressed="true">FQDN</button>' in response.text
        assert 'class="btn btn-outline-secondary" data-service-link-mode="ip" aria-pressed="false">IP</button>' in response.text
        assert 'homelabster.service-link-mode' in response.text
        assert 'htmx:afterSwap' in response.text
        assert 'link-mode-toggle' not in test_client.get("/admin").text
        assert test_client.get("/static/favicon.ico").status_code == 200
        assert test_client.get("/static/homelabster-icon.svg").status_code == 200


def test_static_assets_use_relative_paths_behind_https_proxy(tmp_path: Path):
    config = tmp_path / "services.yaml"
    config.write_text(
        "version: 1\nservices:\n- id: example\n  name: Example\n"
        "  primary_url: https://example.local\n  fallback_url: http://10.0.0.1\n"
        "  icon:\n    local_filename: default-service.svg\n"
    )
    app = create_app(config)
    app.state.icons._metadata = {}

    with TestClient(app) as client:
        headers = {"x-forwarded-proto": "https"}
        dashboard = client.get("/", headers=headers).text
        grid = client.get("/partials/services", headers=headers).text
        form = client.get("/services/new", headers=headers).text

        for asset in ("favicon.ico", "bootstrap-5.3.8.min.css", "app.css", "homelabster-icon.svg", "htmx-2.0.10.min.js", "bootstrap-5.3.8.bundle.min.js"):
            assert f'"/static/{asset}"' in dashboard
        assert 'src="/static/default-service.svg"' in grid
        assert 'src="/static/default-service.svg"' in form

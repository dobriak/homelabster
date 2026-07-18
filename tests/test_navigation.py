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
        assert 'rel="icon" href="http://testserver/static/favicon.ico"' in response.text
        assert 'class="navbar-logo" src="http://testserver/static/homelabster-icon.svg"' in response.text
        assert 'class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main-navigation"' in response.text
        assert 'class="collapse navbar-collapse" id="main-navigation"' in response.text
        assert 'navbar-actions d-flex align-items-center gap-3 ms-auto navbar-actions-with-search' in response.text
        assert test_client.get("/static/favicon.ico").status_code == 200
        assert test_client.get("/static/homelabster-icon.svg").status_code == 200

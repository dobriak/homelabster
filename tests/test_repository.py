from pathlib import Path

import pytest

from homelabster.models import AppSettings, Service
from homelabster.repository import ConfigurationError, ServicesRepository


def service(service_id: str = "grafana") -> Service:
    return Service(id=service_id, name="Grafana", primary_url="https://grafana.local", fallback_url="http://10.0.0.2:3000")


def test_repository_persists_services_atomically(tmp_path: Path):
    path = tmp_path / "services.yaml"
    path.write_text("version: 1\nservices: []\n")
    repo = ServicesRepository(path)
    repo.create(service())

    assert repo.get("grafana").name == "Grafana"
    assert "grafana" in path.read_text()
    assert not list(tmp_path.glob(".services-*.yaml"))


def test_repository_persists_settings_and_defaults_old_config(tmp_path: Path):
    path = tmp_path / "services.yaml"
    path.write_text("version: 1\nservices: []\n")
    repo = ServicesRepository(path)
    assert repo.load().settings.theme == "system"

    repo.update_settings(AppSettings(dashboard_title="Rack", theme="light", health_check_interval_seconds=60))
    loaded = repo.load().settings
    assert loaded.dashboard_title == "Rack"
    assert loaded.theme == "light"
    assert loaded.health_check_interval_seconds == 60


def test_repository_rejects_malformed_and_duplicate_configuration(tmp_path: Path):
    path = tmp_path / "services.yaml"
    path.write_text("services: [not valid")
    with pytest.raises(ConfigurationError, match="invalid YAML"):
        ServicesRepository(path).load()

    path.write_text("version: 1\nservices:\n- id: one\n  name: One\n  primary_url: https://one.local\n  fallback_url: http://10.0.0.1\n- id: one\n  name: Two\n  primary_url: https://two.local\n  fallback_url: http://10.0.0.2\n")
    with pytest.raises(ConfigurationError, match="unique"):
        ServicesRepository(path).load()


def test_repository_missing_config_is_clear(tmp_path: Path):
    with pytest.raises(ConfigurationError, match="missing"):
        ServicesRepository(tmp_path / "nope.yaml").load()

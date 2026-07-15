from pathlib import Path

import pytest

from homelabster.models import ALL_CATEGORY, AppSettings, CategoriesDocument, Category, Service
from homelabster.repository import CategoriesRepository, ConfigurationError, ServicesRepository


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


def test_categories_are_separate_and_keep_all_category(tmp_path: Path):
    path = tmp_path / "categories.yaml"
    repo = CategoriesRepository(path)
    repo.ensure_exists()
    assert repo.list() == [ALL_CATEGORY]

    repo.create(Category(name="Apps", icon="fas fa-cubes", display_order=99))
    assert [category.name for category in repo.list()] == ["All", "Apps"]
    assert repo.get("Apps").display_order == 1
    assert "fa-solid fa-asterisk" in path.read_text()

    with pytest.raises(ValueError, match="reserved"):
        repo.create(Category(name="All", icon="fa-solid fa-asterisk", display_order=0))
    with pytest.raises(ValueError, match="consecutive"):
        CategoriesDocument.model_validate(
            {"categories": [{"name": "All", "icon": "fa-solid fa-asterisk", "display_order": 0}, {"name": "Bad", "icon": "fas fa-x", "display_order": 2}]}
        )

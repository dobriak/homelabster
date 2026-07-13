from __future__ import annotations

import os
import tempfile
from pathlib import Path

import yaml
from pydantic import ValidationError

from .models import AppSettings, Service, ServicesDocument


class ConfigurationError(RuntimeError):
    """A human-readable YAML configuration error."""


class ServicesRepository:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.icons_dir = config_path.parent / "icons"

    def load(self) -> ServicesDocument:
        try:
            with self.config_path.open(encoding="utf-8") as handle:
                raw = yaml.safe_load(handle) or {}
        except FileNotFoundError as exc:
            raise ConfigurationError(f"Services configuration is missing: {self.config_path}") from exc
        except yaml.YAMLError as exc:
            raise ConfigurationError(f"Services configuration contains invalid YAML: {exc}") from exc
        try:
            return ServicesDocument.model_validate(raw)
        except ValidationError as exc:
            raise ConfigurationError(f"Services configuration is invalid: {exc}") from exc

    def save(self, document: ServicesDocument) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        payload = yaml.safe_dump(
            document.model_dump(mode="json", exclude_none=True), sort_keys=False, allow_unicode=True
        )
        fd, temporary_name = tempfile.mkstemp(prefix=".services-", suffix=".yaml", dir=self.config_path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, self.config_path)
        except Exception:
            Path(temporary_name).unlink(missing_ok=True)
            raise

    def list(self) -> list[Service]:
        return self.load().services

    def get(self, service_id: str) -> Service:
        for service in self.list():
            if service.id == service_id:
                return service
        raise KeyError(service_id)

    def create(self, service: Service) -> None:
        document = self.load()
        if any(item.id == service.id for item in document.services):
            raise ValueError("A service with this ID already exists")
        document.services.append(service)
        self.save(document)

    def update(self, original_id: str, service: Service) -> None:
        document = self.load()
        for index, item in enumerate(document.services):
            if item.id == original_id:
                if service.id != original_id and any(s.id == service.id for s in document.services):
                    raise ValueError("A service with this ID already exists")
                document.services[index] = service
                self.save(document)
                return
        raise KeyError(original_id)

    def delete(self, service_id: str) -> None:
        document = self.load()
        remaining = [item for item in document.services if item.id != service_id]
        if len(remaining) == len(document.services):
            raise KeyError(service_id)
        document.services = remaining
        self.save(document)

    def update_settings(self, settings: AppSettings) -> None:
        document = self.load()
        document.settings = settings
        self.save(document)

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import yaml
from pydantic import ValidationError

from .models import ALL_CATEGORY, AppSettings, CategoriesDocument, Category, Service, ServicesDocument


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

    def replace_category(self, original_name: str, new_name: str | None) -> None:
        document = self.load()
        for service in document.services:
            if service.category == original_name:
                service.category = new_name
        self.save(document)

    def assign_categories(self, assignments: dict[str, str | None]) -> None:
        document = self.load()
        existing_ids = {service.id for service in document.services}
        if set(assignments) != existing_ids:
            raise ValueError("Every service must have a category assignment")
        for service in document.services:
            service.category = assignments[service.id]
        self.save(document)


class CategoriesRepository:
    def __init__(self, config_path: Path):
        self.config_path = config_path

    def load(self) -> CategoriesDocument:
        try:
            with self.config_path.open(encoding="utf-8") as handle:
                raw = yaml.safe_load(handle) or {}
        except FileNotFoundError:
            return CategoriesDocument()
        except yaml.YAMLError as exc:
            raise ConfigurationError(f"Categories configuration contains invalid YAML: {exc}") from exc
        try:
            return CategoriesDocument.model_validate(raw)
        except ValidationError as exc:
            raise ConfigurationError(f"Categories configuration is invalid: {exc}") from exc

    def save(self, document: CategoriesDocument) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        payload = yaml.safe_dump(
            document.model_dump(mode="json", exclude_none=True), sort_keys=False, allow_unicode=True
        )
        fd, temporary_name = tempfile.mkstemp(prefix=".categories-", suffix=".yaml", dir=self.config_path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, self.config_path)
        except Exception:
            Path(temporary_name).unlink(missing_ok=True)
            raise

    def ensure_exists(self) -> None:
        if not self.config_path.exists():
            self.save(CategoriesDocument())

    def list(self) -> list[Category]:
        return sorted(self.load().categories, key=lambda category: category.display_order)

    def get(self, name: str) -> Category:
        for category in self.list():
            if category.name == name:
                return category
        raise KeyError(name)

    def create(self, category: Category) -> None:
        if category.name == "All":
            raise ValueError('"All" is a reserved category')
        document = self.load()
        if any(item.name.casefold() == category.name.casefold() for item in document.categories):
            raise ValueError("A category with this name already exists")
        category.display_order = len(document.categories)
        document.categories.append(category)
        self.save(document)

    def update(self, original_name: str, category: Category) -> None:
        if original_name == "All" or category.name == "All":
            raise ValueError('"All" is a reserved category')
        document = self.load()
        for index, item in enumerate(document.categories):
            if item.name == original_name:
                if category.name.casefold() != original_name.casefold() and any(
                    existing.name.casefold() == category.name.casefold() for existing in document.categories
                ):
                    raise ValueError("A category with this name already exists")
                category.display_order = item.display_order
                document.categories[index] = category
                self.save(document)
                return
        raise KeyError(original_name)

    def delete(self, name: str) -> None:
        if name == "All":
            raise ValueError('"All" cannot be deleted')
        document = self.load()
        remaining = [item for item in document.categories if item.name != name]
        if len(remaining) == len(document.categories):
            raise KeyError(name)
        for index, category in enumerate((category for category in remaining if category.name != "All"), start=1):
            category.display_order = index
        document.categories = remaining
        self.save(document)

    def reorder(self, order: list[str]) -> None:
        document = self.load()
        existing = [category.name for category in document.categories if category.name != "All"]
        if len(order) != len(existing) or set(order) != set(existing):
            raise ValueError("Every category must have a display order")
        by_name = {category.name: category for category in document.categories}
        for index, name in enumerate(order, start=1):
            by_name[name].display_order = index
        document.categories = [ALL_CATEGORY, *(by_name[name] for name in order)]
        self.save(document)

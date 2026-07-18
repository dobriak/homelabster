from __future__ import annotations

import re
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


def _validate_http_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("must be an absolute http or https URL")
    return value


class Icon(BaseModel):
    source_slug: str | None = None
    local_filename: str | None = None

    @field_validator("local_filename")
    @classmethod
    def safe_filename(cls, value: str | None) -> str | None:
        if value and ("/" in value or "\\" in value or value in {".", ".."}):
            raise ValueError("must be a plain filename")
        return value


class Service(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    name: str = Field(min_length=1, max_length=100)
    primary_url: str
    fallback_url: str
    health_url: str | None = None
    icon: Icon = Field(default_factory=Icon)
    category: str | None = None

    @field_validator("primary_url", "fallback_url", "health_url")
    @classmethod
    def http_urls(cls, value: str | None) -> str | None:
        return _validate_http_url(value) if value else value

    @field_validator("category")
    @classmethod
    def clean_category(cls, value: str | None) -> str | None:
        return value.strip() or None if value else None


class AppSettings(BaseModel):
    dashboard_title: str = Field(default="Homelabster", min_length=1, max_length=120)
    theme: Literal["system", "light", "dark"] = "system"
    health_checks_enabled: bool = True
    health_check_interval_seconds: int = Field(default=30, ge=5, le=3600)


class ServicesDocument(BaseModel):
    version: int = 1
    settings: AppSettings = Field(default_factory=AppSettings)
    services: list[Service] = Field(default_factory=list)

    @field_validator("services")
    @classmethod
    def unique_ids(cls, services: list[Service]) -> list[Service]:
        ids = [service.id for service in services]
        if len(ids) != len(set(ids)):
            raise ValueError("service IDs must be unique")
        return services


class Category(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    icon: str = Field(min_length=1, max_length=100)
    display_order: int = Field(ge=0)

    @field_validator("name", "icon")
    @classmethod
    def non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("name")
    @classmethod
    def route_safe_name(cls, value: str) -> str:
        if "/" in value or "?" in value or "#" in value:
            raise ValueError("must not contain /, ?, or #")
        return value

    @field_validator("icon")
    @classmethod
    def free_font_awesome_icon(cls, value: str) -> str:
        style, *rest = value.split()
        if style not in {"fas", "far", "fab", "fa-solid", "fa-regular", "fa-brands"} or len(rest) != 1 or not rest[0].startswith("fa-"):
            raise ValueError("must be a free Font Awesome icon class pair, such as 'fas fa-cloud'")
        return value


ALL_CATEGORY = Category(name="All", icon="fa-solid fa-asterisk", display_order=0)


class CategoriesDocument(BaseModel):
    version: int = 1
    categories: list[Category] = Field(default_factory=lambda: [ALL_CATEGORY])

    @field_validator("categories")
    @classmethod
    def valid_categories(cls, categories: list[Category]) -> list[Category]:
        names = [category.name.casefold() for category in categories]
        if len(names) != len(set(names)):
            raise ValueError("category names must be unique")

        all_categories = [category for category in categories if category.name == "All"]
        if all_categories != [ALL_CATEGORY]:
            raise ValueError('the "All" category must have icon "fa-solid fa-asterisk" and display_order 0')

        other_orders = sorted(category.display_order for category in categories if category.name != "All")
        if other_orders != list(range(1, len(other_orders) + 1)):
            raise ValueError("category display_order values must start at 1 and be consecutive")
        return categories


def service_id_from_name(name: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return value

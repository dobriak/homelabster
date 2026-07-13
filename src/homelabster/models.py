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

    @field_validator("primary_url", "fallback_url", "health_url")
    @classmethod
    def http_urls(cls, value: str | None) -> str | None:
        return _validate_http_url(value) if value else value


class AppSettings(BaseModel):
    dashboard_title: str = Field(default="Homelabster", min_length=1, max_length=120)
    theme: Literal["system", "light", "dark"] = "system"
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


def service_id_from_name(name: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return value

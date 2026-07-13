from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any

import httpx


METADATA_URL = "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/metadata.json"
CDN_URL = "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/{format}/{slug}.{format}"
ALLOWED_EXTENSIONS = {".svg", ".png", ".webp"}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


class IconManager:
    def __init__(self, icons_dir: Path, metadata_url: str = METADATA_URL, cdn_url: str = CDN_URL):
        self.icons_dir = icons_dir
        self.metadata_url = metadata_url
        self.cdn_url = cdn_url
        self._metadata: dict[str, Any] | None = None

    async def metadata(self) -> dict[str, Any]:
        if self._metadata is None:
            async with httpx.AsyncClient(timeout=8) as client:
                response = await client.get(self.metadata_url)
                response.raise_for_status()
                data = response.json()
            self._metadata = data.get("icons", data) if isinstance(data, dict) else {}
        return self._metadata

    @staticmethod
    def _aliases(entry: Any) -> list[str]:
        if not isinstance(entry, dict):
            return []
        aliases = entry.get("aliases", entry.get("alias", []))
        if isinstance(aliases, str):
            return [aliases]
        return [item for item in aliases if isinstance(item, str)] if isinstance(aliases, list) else []

    async def find(self, name: str) -> tuple[str, dict[str, Any]] | None:
        wanted = normalize(name)
        metadata = await self.metadata()
        for slug, entry in metadata.items():
            if normalize(str(slug)) == wanted:
                return str(slug), entry if isinstance(entry, dict) else {}
        for slug, entry in metadata.items():
            if any(normalize(alias) == wanted for alias in self._aliases(entry)):
                return str(slug), entry if isinstance(entry, dict) else {}
        return None

    @staticmethod
    def _format(entry: dict[str, Any]) -> str:
        # Dashboard Icons calls this field `base`; retain `format` support for
        # compatible catalog versions and tests.
        value = entry.get("base", entry.get("format", "svg"))
        if isinstance(value, list):
            value = value[0] if value else "svg"
        return value if value in {"svg", "png", "webp"} else "svg"

    async def resolve(self, name: str) -> tuple[str, str] | None:
        match = await self.find(name)
        if not match:
            return None
        slug, entry = match
        image_format = self._format(entry)
        variants = entry.get("colors", entry.get("variants", {}))
        variant = variants.get("light") if isinstance(variants, dict) else None
        source_slug = str(variant or slug)
        filename = f"{normalize(slug)}-{uuid.uuid4().hex[:8]}.{image_format}"
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(self.cdn_url.format(format=image_format, slug=source_slug))
            response.raise_for_status()
        (self.icons_dir / filename).write_bytes(response.content)
        return source_slug, filename

    def save_upload(self, filename: str | None, content: bytes) -> str:
        extension = Path(filename or "").suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("Icon must be an SVG, PNG, or WEBP file")
        if not content:
            raise ValueError("Uploaded icon is empty")
        if len(content) > 2 * 1024 * 1024:
            raise ValueError("Icon must be smaller than 2 MiB")
        if extension == ".svg" and b"<svg" not in content[:1024].lower():
            raise ValueError("Uploaded SVG is invalid")
        if extension == ".png" and not content.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("Uploaded PNG is invalid")
        if extension == ".webp" and not (content.startswith(b"RIFF") and content[8:12] == b"WEBP"):
            raise ValueError("Uploaded WEBP is invalid")
        stored = f"upload-{uuid.uuid4().hex}{extension}"
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        (self.icons_dir / stored).write_bytes(content)
        return stored

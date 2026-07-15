from pathlib import Path

import pytest

from homelabster.icons import IconManager


@pytest.mark.asyncio
async def test_icon_match_prefers_slug_then_alias(tmp_path: Path):
    manager = IconManager(tmp_path)
    manager._metadata = {"home-assistant": {"aliases": ["HASS"]}, "other": {"aliases": ["Home Assistant"]}}
    assert (await manager.find("Home Assistant"))[0] == "home-assistant"
    assert (await manager.find("hass"))[0] == "home-assistant"


@pytest.mark.asyncio
async def test_preview_url_uses_light_variant(tmp_path: Path):
    manager = IconManager(tmp_path, cdn_url="https://icons.test/{format}/{slug}.{format}")
    manager._metadata = {"grafana": {"base": "svg", "colors": {"light": "grafana-light"}}}
    assert await manager.preview_url("Grafana") == "https://icons.test/svg/grafana-light.svg"


def test_upload_validation_and_storage(tmp_path: Path):
    manager = IconManager(tmp_path)
    stored = manager.save_upload("logo.svg", b"<svg xmlns='http://www.w3.org/2000/svg'></svg>")
    assert (tmp_path / stored).exists()
    with pytest.raises(ValueError, match="SVG"):
        manager.save_upload("logo.svg", b"not an image")
    with pytest.raises(ValueError, match="SVG, PNG, or WEBP"):
        manager.save_upload("logo.gif", b"GIF89a")


def test_catalog_metadata_base_and_light_variant(tmp_path: Path):
    manager = IconManager(tmp_path)
    assert manager._format({"base": "png"}) == "png"
    assert manager._format({"base": "unexpected"}) == "svg"

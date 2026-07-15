# Repository Guidelines

## Project Structure & Module Organization

Homelabster is a local-first FastAPI dashboard for YAML-defined homelab services. Application code lives in `src/homelabster/`: `main.py` defines routes and app setup, `models.py` contains Pydantic models, and `repository.py`, `health.py`, and `icons.py` hold persistence and service logic. Server-rendered Jinja templates are in `src/homelabster/templates/`, with reusable fragments in `templates/partials/`; local Bootstrap, htmx, CSS, and fallback SVG assets are in `static/`.

Tests mirror feature areas under `tests/`. Versioned configuration examples live in `config/*.yaml.example`; never commit local `config/services.yaml`, `config/categories.yaml`, or `config/icons/` content.

## Build, Test, and Development Commands

```sh
uv sync --group dev                 # install app and test dependencies
cp config/services.yaml.example config/services.yaml
cp config/categories.yaml.example config/categories.yaml
uv run fastapi dev src/homelabster/main.py  # start local server
uv run pytest                       # run the full test suite
```

To keep runtime data outside the checkout, set `HOMELABSTER_DATA_DIR` and place both YAML files there.

## Coding Style & Naming Conventions

Target Python 3.11+ and follow the existing style: four-space indentation, type annotations for public functions, `snake_case` for functions and variables, `PascalCase` for classes, and concise module-level constants in `UPPER_SNAKE_CASE`. Keep routes thin and place validation/persistence behavior in models or repositories. Match the existing Jinja and HTML formatting; name reusable template fragments descriptively, such as `service_form.html`.

No formatter or linter is configured, so make focused edits and preserve nearby formatting.

## Testing Guidelines

Use pytest with `pytest-asyncio` (configured with `asyncio_mode = "auto"`). Name files `test_*.py` and tests `test_<behavior>`. Use `tmp_path` for YAML-backed tests so repository configuration is never touched. Cover both successful request flows and validation/error responses; run `uv run pytest` before opening a PR.

## Commit & Pull Request Guidelines

Existing history uses short, imperative, title-cased subjects (for example, `Adding categories`); follow that pattern and keep commits scoped. Pull requests should explain the user-visible change, list tests run, link relevant issues, and include screenshots for dashboard or template changes. Call out configuration or migration implications explicitly.

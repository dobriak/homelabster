from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from .health import HealthMonitor
from .icons import IconManager
from .models import AppSettings, Icon, Service, service_id_from_name
from .repository import ConfigurationError, ServicesRepository

PACKAGE_DIR = Path(__file__).parent
PROJECT_DIR = PACKAGE_DIR.parents[1]


def configured_path() -> Path:
    data_dir = os.getenv("HOMELABSTER_DATA_DIR")
    if data_dir:
        return Path(data_dir) / "services.yaml"
    return Path(os.getenv("HOMELABSTER_CONFIG", PROJECT_DIR / "config" / "services.yaml"))


async def _poll_forever(app: FastAPI) -> None:
    while True:
        try:
            document = app.state.repository.load()
            await app.state.monitor.poll(document.services)
            interval = document.settings.health_check_interval_seconds
        except ConfigurationError:
            interval = 30
        await asyncio.sleep(interval)


def create_app(config_path: Path | None = None) -> FastAPI:
    repository = ServicesRepository(config_path or configured_path())
    repository.icons_dir.mkdir(parents=True, exist_ok=True)
    monitor = HealthMonitor()
    icons = IconManager(repository.icons_dir)
    templates = Jinja2Templates(directory=str(PACKAGE_DIR / "templates"))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(_poll_forever(app))
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    app = FastAPI(title="Homelabster", lifespan=lifespan)
    app.state.repository = repository
    app.state.monitor = monitor
    app.state.icons = icons
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
    app.mount("/icons", StaticFiles(directory=repository.icons_dir), name="icons")

    def context(request: Request, **values: object) -> dict[str, object]:
        return {"request": request, "monitor": monitor, "settings": AppSettings(), **values}

    def render_grid(request: Request) -> HTMLResponse:
        try:
            services = repository.list()
            return templates.TemplateResponse(request, "partials/service_grid.html", context(request, services=services))
        except ConfigurationError as exc:
            return templates.TemplateResponse(request, "partials/config_error.html", context(request, error=str(exc)), status_code=500)

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        try:
            settings = repository.load().settings
            return templates.TemplateResponse(request, "dashboard.html", context(request, settings=settings))
        except ConfigurationError as exc:
            return templates.TemplateResponse(request, "dashboard.html", context(request, error=str(exc)), status_code=500)

    @app.get("/partials/services", response_class=HTMLResponse)
    async def service_grid(request: Request):
        return render_grid(request)

    @app.get("/admin", response_class=HTMLResponse)
    async def admin(request: Request):
        try:
            settings = repository.load().settings
            return templates.TemplateResponse(request, "admin.html", context(request, settings=settings))
        except ConfigurationError as exc:
            return templates.TemplateResponse(request, "admin.html", context(request, error=str(exc)), status_code=500)

    @app.post("/admin/settings", response_class=HTMLResponse)
    async def update_settings(
        request: Request,
        dashboard_title: str = Form(""),
        theme: str = Form("system"),
        health_check_interval_seconds: str = Form("30"),
    ):
        try:
            settings = AppSettings(
                dashboard_title=dashboard_title.strip(),
                theme=theme,
                health_check_interval_seconds=health_check_interval_seconds,
            )
            repository.update_settings(settings)
        except (ValidationError, ValueError, ConfigurationError) as exc:
            return templates.TemplateResponse(
                request, "partials/settings_form.html", context(request, error=str(exc)), status_code=422
            )
        response = templates.TemplateResponse(request, "partials/settings_form.html", context(request, settings=settings, saved=True))
        response.headers["HX-Refresh"] = "true"
        return response

    @app.get("/services", response_class=HTMLResponse)
    async def services(request: Request):
        try:
            document = repository.load()
            return templates.TemplateResponse(request, "services.html", context(request, settings=document.settings, services=document.services))
        except ConfigurationError as exc:
            return templates.TemplateResponse(request, "services.html", context(request, error=str(exc), services=[]), status_code=500)

    @app.get("/services/new", response_class=HTMLResponse)
    async def new_service_form(request: Request):
        return templates.TemplateResponse(request, "partials/service_form.html", context(request, service=None, action="/services"))

    @app.get("/services/{service_id}/edit", response_class=HTMLResponse)
    async def edit_service_form(request: Request, service_id: str):
        try:
            service = repository.get(service_id)
        except KeyError:
            raise HTTPException(404, "Service not found")
        return templates.TemplateResponse(request, "partials/service_form.html", context(request, service=service, action=f"/services/{service_id}"))

    async def build_service(
        name: str,
        service_id: str,
        primary_url: str,
        fallback_url: str,
        health_url: str,
        upload: UploadFile | None,
        previous: Service | None = None,
    ) -> Service:
        service_id = service_id.strip() or service_id_from_name(name)
        current_icon = previous.icon if previous else Icon(local_filename="default-service.svg")
        try:
            if upload and upload.filename:
                current_icon = Icon(local_filename=icons.save_upload(upload.filename, await upload.read()))
            elif previous is None or name.strip() != previous.name:
                try:
                    resolved = await icons.resolve(name)
                except Exception:
                    resolved = None
                if resolved:
                    current_icon = Icon(source_slug=resolved[0], local_filename=resolved[1])
            return Service(
                id=service_id,
                name=name.strip(),
                primary_url=primary_url.strip(),
                fallback_url=fallback_url.strip(),
                health_url=health_url.strip() or None,
                icon=current_icon,
            )
        except (ValidationError, ValueError) as exc:
            raise ValueError(str(exc)) from exc

    def invalid_form(request: Request, service: Service | None, action: str, error: str) -> HTMLResponse:
        response = templates.TemplateResponse(
            request, "partials/service_form.html", context(request, service=service, action=action, error=error), status_code=422
        )
        response.headers["HX-Retarget"] = "#service-form-slot"
        response.headers["HX-Reswap"] = "innerHTML"
        return response

    @app.post("/services", response_class=HTMLResponse)
    async def create_service(
        request: Request,
        name: str = Form(...),
        service_id: str = Form(""),
        primary_url: str = Form(...),
        fallback_url: str = Form(...),
        health_url: str = Form(""),
        icon_upload: UploadFile | None = File(None),
    ):
        try:
            service = await build_service(name, service_id, primary_url, fallback_url, health_url, icon_upload)
            repository.create(service)
        except (ValueError, ConfigurationError) as exc:
            return invalid_form(request, None, "/services", str(exc))
        return templates.TemplateResponse(request, "partials/service_row.html", context(request, service=service))

    @app.put("/services/{original_id}", response_class=HTMLResponse)
    async def update_service(
        request: Request,
        original_id: str,
        name: str = Form(...),
        service_id: str = Form(""),
        primary_url: str = Form(...),
        fallback_url: str = Form(...),
        health_url: str = Form(""),
        icon_upload: UploadFile | None = File(None),
    ):
        try:
            previous = repository.get(original_id)
            service = await build_service(name, service_id, primary_url, fallback_url, health_url, icon_upload, previous)
            repository.update(original_id, service)
        except KeyError:
            raise HTTPException(404, "Service not found")
        except (ValueError, ConfigurationError) as exc:
            return invalid_form(request, None, f"/services/{original_id}", str(exc))
        return templates.TemplateResponse(request, "partials/service_row.html", context(request, service=service))

    @app.delete("/services/{service_id}", response_class=HTMLResponse)
    async def delete_service(service_id: str):
        try:
            repository.delete(service_id)
        except KeyError:
            raise HTTPException(404, "Service not found")
        return HTMLResponse("")

    return app


app = create_app()

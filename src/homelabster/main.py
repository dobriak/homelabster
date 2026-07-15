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
from .models import AppSettings, Category, Icon, Service, service_id_from_name
from .repository import CategoriesRepository, ConfigurationError, ServicesRepository

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
    categories = CategoriesRepository(repository.config_path.parent / "categories.yaml")
    categories.ensure_exists()
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
    app.state.categories = categories
    app.state.monitor = monitor
    app.state.icons = icons
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
    app.mount("/icons", StaticFiles(directory=repository.icons_dir), name="icons")

    def context(request: Request, **values: object) -> dict[str, object]:
        return {"request": request, "monitor": monitor, "settings": AppSettings(), **values}

    def render_grid(request: Request) -> HTMLResponse:
        try:
            services = repository.list()
            category_list = categories.list()
            category_names = {category.name for category in category_list}
            unknown_categories = sorted({service.category for service in services if service.category and service.category not in category_names})
            if unknown_categories:
                raise ConfigurationError(f"Services reference missing categories: {', '.join(unknown_categories)}")
            return templates.TemplateResponse(
                request, "partials/service_grid.html", context(request, services=services, categories=category_list)
            )
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
            return templates.TemplateResponse(
                request,
                "admin.html",
                context(request, settings=settings, categories=categories.list(), services=repository.list()),
            )
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
            return templates.TemplateResponse(
                request, "services.html", context(request, settings=document.settings, services=document.services, categories=categories.list())
            )
        except ConfigurationError as exc:
            return templates.TemplateResponse(request, "services.html", context(request, error=str(exc), services=[]), status_code=500)

    @app.get("/services/new", response_class=HTMLResponse)
    async def new_service_form(request: Request):
        return templates.TemplateResponse(
            request, "partials/service_form.html", context(request, service=None, action="/services", categories=categories.list())
        )

    @app.get("/services/{service_id}/edit", response_class=HTMLResponse)
    async def edit_service_form(request: Request, service_id: str):
        try:
            service = repository.get(service_id)
        except KeyError:
            raise HTTPException(404, "Service not found")
        return templates.TemplateResponse(
            request,
            "partials/service_form.html",
            context(request, service=service, action=f"/services/{service_id}", categories=categories.list()),
        )

    async def build_service(
        name: str,
        service_id: str,
        primary_url: str,
        fallback_url: str,
        health_url: str,
        category: str,
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
            category = category.strip() or None
            if category == "All" or (category and category not in {item.name for item in categories.list()}):
                raise ValueError("Select an existing category or leave the service unassigned")
            return Service(
                id=service_id,
                name=name.strip(),
                primary_url=primary_url.strip(),
                fallback_url=fallback_url.strip(),
                health_url=health_url.strip() or None,
                icon=current_icon,
                category=category,
            )
        except (ValidationError, ValueError) as exc:
            raise ValueError(str(exc)) from exc

    def invalid_form(request: Request, service: Service | None, action: str, error: str) -> HTMLResponse:
        response = templates.TemplateResponse(
            request,
            "partials/service_form.html",
            context(request, service=service, action=action, categories=categories.list(), error=error),
            status_code=422,
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
        category: str = Form(""),
        icon_upload: UploadFile | None = File(None),
    ):
        try:
            service = await build_service(name, service_id, primary_url, fallback_url, health_url, category, icon_upload)
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
        category: str = Form(""),
        icon_upload: UploadFile | None = File(None),
    ):
        try:
            previous = repository.get(original_id)
            service = await build_service(name, service_id, primary_url, fallback_url, health_url, category, icon_upload, previous)
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

    def invalid_category_form(request: Request, category: Category | None, action: str, error: str) -> HTMLResponse:
        response = templates.TemplateResponse(
            request,
            "partials/category_form.html",
            context(request, category=category, action=action, error=error),
            status_code=422,
        )
        response.headers["HX-Retarget"] = "#category-form-slot"
        response.headers["HX-Reswap"] = "innerHTML"
        return response

    def build_category(name: str, icon: str) -> Category:
        return Category(name=name, icon=icon, display_order=1)

    @app.get("/admin/categories/new", response_class=HTMLResponse)
    async def new_category_form(request: Request):
        return templates.TemplateResponse(
            request, "partials/category_form.html", context(request, category=None, action="/admin/categories")
        )

    @app.get("/admin/categories/{name}/edit", response_class=HTMLResponse)
    async def edit_category_form(request: Request, name: str):
        try:
            category = categories.get(name)
        except KeyError:
            raise HTTPException(404, "Category not found")
        if category.name == "All":
            raise HTTPException(400, 'The "All" category cannot be edited')
        return templates.TemplateResponse(
            request, "partials/category_form.html", context(request, category=category, action=f"/admin/categories/{name}")
        )

    @app.post("/admin/categories", response_class=HTMLResponse)
    async def create_category(request: Request, name: str = Form(...), icon: str = Form(...)):
        try:
            categories.create(build_category(name, icon))
        except (ValidationError, ValueError, ConfigurationError) as exc:
            return invalid_category_form(request, None, "/admin/categories", str(exc))
        response = HTMLResponse("")
        response.headers["HX-Refresh"] = "true"
        return response

    @app.put("/admin/categories/{original_name}", response_class=HTMLResponse)
    async def update_category(request: Request, original_name: str, name: str = Form(...), icon: str = Form(...)):
        try:
            category = build_category(name, icon)
            categories.update(original_name, category)
            if category.name != original_name:
                repository.replace_category(original_name, category.name)
        except KeyError:
            raise HTTPException(404, "Category not found")
        except (ValidationError, ValueError, ConfigurationError) as exc:
            return invalid_category_form(request, None, f"/admin/categories/{original_name}", str(exc))
        response = HTMLResponse("")
        response.headers["HX-Refresh"] = "true"
        return response

    @app.delete("/admin/categories/{name}", response_class=HTMLResponse)
    async def delete_category(name: str):
        try:
            categories.delete(name)
            repository.replace_category(name, None)
        except KeyError:
            raise HTTPException(404, "Category not found")
        except (ValueError, ConfigurationError) as exc:
            raise HTTPException(422, str(exc)) from exc
        response = HTMLResponse("")
        response.headers["HX-Refresh"] = "true"
        return response

    @app.post("/admin/categories/order", response_class=HTMLResponse)
    async def reorder_categories(category_name: list[str] = Form([]), display_order: list[str] = Form([])):
        try:
            if len(category_name) != len(display_order):
                raise ValueError("Every category must have a display order")
            positions = [int(value) for value in display_order]
            if sorted(positions) != list(range(1, len(category_name) + 1)):
                raise ValueError("Display order must use each number from 1 to the number of categories once")
            categories.reorder([name for _, name in sorted(zip(positions, category_name))])
        except (ValueError, ConfigurationError) as exc:
            return HTMLResponse(f'<div class="alert alert-danger">{exc}</div>', status_code=422)
        response = HTMLResponse("")
        response.headers["HX-Refresh"] = "true"
        return response

    @app.post("/admin/service-categories", response_class=HTMLResponse)
    async def assign_service_categories(service_id: list[str] = Form([]), category: list[str] = Form([])):
        try:
            if len(service_id) != len(category):
                raise ValueError("Every service must have a category assignment")
            valid_categories = {item.name for item in categories.list() if item.name != "All"}
            assignments = dict(zip(service_id, category))
            if len(assignments) != len(service_id) or any(value and value not in valid_categories for value in assignments.values()):
                raise ValueError("Select an existing category or leave the service unassigned")
            repository.assign_categories({service: assigned or None for service, assigned in assignments.items()})
        except (ValueError, ConfigurationError) as exc:
            return HTMLResponse(f'<div class="alert alert-danger">{exc}</div>', status_code=422)
        response = HTMLResponse("")
        response.headers["HX-Refresh"] = "true"
        return response

    return app


app = create_app()

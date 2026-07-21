from __future__ import annotations

import asyncio
import json
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
from .models import AppSettings, Category, Icon, IpamDocument, IpamHost, IpamNetwork, IpamPort, Service, service_id_from_name
from .repository import CategoriesRepository, ConfigurationError, IpamRepository, ServicesRepository

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
            interval = document.settings.health_check_interval_seconds
            if document.settings.health_checks_enabled:
                await app.state.monitor.poll(document.services)
        except ConfigurationError:
            interval = 30
        await asyncio.sleep(interval)


def create_app(config_path: Path | None = None) -> FastAPI:
    repository = ServicesRepository(config_path or configured_path())
    categories = CategoriesRepository(repository.config_path.parent / "categories.yaml")
    categories.ensure_exists()
    repository.icons_dir.mkdir(parents=True, exist_ok=True)
    ipam = IpamRepository(repository.config_path.parent / "ipam.yaml")
    ipam.ensure_exists()
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
    app.state.ipam = ipam
    app.state.monitor = monitor
    app.state.icons = icons
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
    app.mount("/icons", StaticFiles(directory=repository.icons_dir), name="icons")

    def context(request: Request, **values: object) -> dict[str, object]:
        return {"request": request, "monitor": monitor, "settings": AppSettings(), **values}

    def render_grid(request: Request, search: str = "") -> HTMLResponse:
        try:
            document = repository.load()
            services = document.services
            category_list = categories.list()
            category_names = {category.name for category in category_list}
            unknown_categories = sorted({service.category for service in services if service.category and service.category not in category_names})
            if unknown_categories:
                raise ConfigurationError(f"Services reference missing categories: {', '.join(unknown_categories)}")
            search = search.strip()
            if search:
                normalized_search = search.casefold()
                services = [service for service in services if normalized_search in service.name.casefold()]
            return templates.TemplateResponse(
                request,
                "partials/service_grid.html",
                context(request, settings=document.settings, services=services, categories=category_list, search=search),
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
    async def service_grid(request: Request, search: str = ""):
        return render_grid(request, search)

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
        health_checks_enabled: bool = Form(True),
        health_check_interval_seconds: str = Form("30"),
    ):
        try:
            settings = AppSettings(
                dashboard_title=dashboard_title.strip(),
                theme=theme,
                health_checks_enabled=health_checks_enabled,
                health_check_interval_seconds=health_check_interval_seconds,
            )
            repository.update_settings(settings)
            if not settings.health_checks_enabled:
                monitor.statuses.clear()
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

    @app.get("/services/icon-preview", response_class=HTMLResponse)
    async def service_icon_preview(request: Request, name: str = "", icon_lookup_name: str = ""):
        try:
            lookup_name = icon_lookup_name.strip() or name.strip()
            preview_url = await icons.preview_url(lookup_name) if lookup_name else None
        except Exception:
            preview_url = None
        return templates.TemplateResponse(
            request, "partials/service_icon_preview.html", context(request, service=None, preview_url=preview_url)
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
        icon_lookup_name: str,
        upload: UploadFile | None,
        previous: Service | None = None,
    ) -> Service:
        service_id = service_id.strip() or service_id_from_name(name)
        icon_name = icon_lookup_name.strip() or name.strip()
        current_icon = previous.icon if previous else Icon(local_filename="default-service.svg")
        try:
            if upload and upload.filename:
                current_icon = Icon(local_filename=icons.save_upload(upload.filename, await upload.read()))
            elif previous is None or name.strip() != previous.name or icon_lookup_name.strip():
                try:
                    resolved = await icons.resolve(icon_name)
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
        response.headers["HX-Trigger"] = json.dumps(
            {"service-save-status": {"message": f"Service was not saved: {error}", "variant": "danger", "clear_form": False}}
        )
        return response

    def saved_service_response(request: Request, service: Service) -> HTMLResponse:
        response = templates.TemplateResponse(request, "partials/service_row.html", context(request, service=service))
        response.headers["HX-Trigger"] = json.dumps(
            {"service-save-status": {"message": f"{service.name} was saved.", "variant": "success", "clear_form": True}}
        )
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
        icon_lookup_name: str = Form(""),
        icon_upload: UploadFile | None = File(None),
    ):
        try:
            service = await build_service(name, service_id, primary_url, fallback_url, health_url, category, icon_lookup_name, icon_upload)
            repository.create(service)
        except (ValueError, ConfigurationError) as exc:
            return invalid_form(request, None, "/services", str(exc))
        return saved_service_response(request, service)

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
        icon_lookup_name: str = Form(""),
        icon_upload: UploadFile | None = File(None),
    ):
        try:
            previous = repository.get(original_id)
            service = await build_service(name, service_id, primary_url, fallback_url, health_url, category, icon_lookup_name, icon_upload, previous)
            repository.update(original_id, service)
        except KeyError:
            raise HTTPException(404, "Service not found")
        except (ValueError, ConfigurationError) as exc:
            return invalid_form(request, None, f"/services/{original_id}", str(exc))
        return saved_service_response(request, service)

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

    # ------------------------------------------------------------------
    # IPAM routes
    # ------------------------------------------------------------------

    @app.get("/ipam", response_class=HTMLResponse)
    async def ipam_page(request: Request):
        try:
            settings = repository.load().settings
            networks = ipam.list_networks()
            return templates.TemplateResponse(
                request, "ipam.html", context(request, settings=settings, networks=networks)
            )
        except ConfigurationError as exc:
            return templates.TemplateResponse(
                request, "ipam.html", context(request, settings=AppSettings(), networks=[], error=str(exc))
            )

    @app.get("/ipam/networks/cancel", response_class=HTMLResponse)
    async def ipam_network_cancel(request: Request):
        return HTMLResponse(
            '<button class="btn btn-primary" hx-get="/ipam/networks/new" hx-target="#ipam-network-form-slot" hx-swap="innerHTML">Add CIDR</button>'
        )

    @app.get("/ipam/networks/new", response_class=HTMLResponse)
    async def ipam_network_new_form(request: Request):
        return templates.TemplateResponse(
            request, "partials/ipam_network_form.html", context(request, network=None)
        )

    @app.get("/ipam/networks/{cidr:path}/edit", response_class=HTMLResponse)
    async def ipam_network_edit_form(request: Request, cidr: str):
        try:
            network = ipam.get_network(cidr)
        except KeyError:
            raise HTTPException(404, "CIDR not found")
        return templates.TemplateResponse(
            request, "partials/ipam_network_form.html", context(request, network=network)
        )

    def _render_network_list(request: Request) -> HTMLResponse:
        networks = ipam.list_networks()
        return templates.TemplateResponse(
            request, "partials/ipam_network_list.html", context(request, networks=networks)
        )

    @app.post("/ipam/networks", response_class=HTMLResponse)
    async def ipam_create_network(request: Request, cidr: str = Form(...)):
        try:
            network = IpamNetwork(cidr=cidr.strip())
            ipam.create_network(network)
        except (ValidationError, ValueError) as exc:
            response = templates.TemplateResponse(
                request,
                "partials/ipam_network_form.html",
                context(request, network=None, error=str(exc)),
                status_code=422,
            )
            response.headers["HX-Retarget"] = "#ipam-network-form-slot"
            return response
        return _render_network_list(request)

    def _render_full_accordion_body(request: Request, cidr: str) -> HTMLResponse:
        try:
            network = ipam.get_network(cidr)
        except KeyError:
            raise HTTPException(404, "CIDR not found")
        return templates.TemplateResponse(
            request,
            "partials/ipam_network_body.html",
            context(request, network=network, net_index=0),
        )

    @app.get("/ipam/networks/{cidr:path}/hosts/new", response_class=HTMLResponse)
    async def ipam_host_new_form(request: Request, cidr: str, net_index: int = 0):
        try:
            network = ipam.get_network(cidr)
        except KeyError:
            raise HTTPException(404, "CIDR not found")
        return templates.TemplateResponse(
            request,
            "partials/ipam_host_form.html",
            context(request, network=network, host=None, net_index=net_index),
        )

    @app.get("/ipam/networks/{cidr:path}/hosts/{ip}/edit", response_class=HTMLResponse)
    async def ipam_host_edit_form(request: Request, cidr: str, ip: str, net_index: int = 0):
        try:
            network = ipam.get_network(cidr)
            host = ipam.get_host(cidr, ip)
        except KeyError:
            raise HTTPException(404, "Host not found")
        return templates.TemplateResponse(
            request,
            "partials/ipam_host_form.html",
            context(request, network=network, host=host, net_index=net_index),
        )

    @app.post("/ipam/networks/{cidr:path}/hosts", response_class=HTMLResponse)
    async def ipam_create_host(request: Request, cidr: str, hostname: str = Form(...), ip: str = Form(...), net_index: int = Form(0)):
        try:
            host = IpamHost(hostname=hostname.strip(), ip=ip.strip())
            ipam.create_host(cidr, host)
        except KeyError:
            raise HTTPException(404, "CIDR not found")
        except (ValidationError, ValueError) as exc:
            try:
                network = ipam.get_network(cidr)
            except KeyError:
                raise HTTPException(404, "CIDR not found")
            response = templates.TemplateResponse(
                request,
                "partials/ipam_host_form.html",
                context(request, network=network, host=IpamHost(hostname=hostname.strip(), ip=ip.strip()), net_index=net_index, error=str(exc)),
                status_code=422,
            )
            return response
        return _render_full_accordion_body(request, cidr, net_index)

    @app.put("/ipam/networks/{cidr:path}/hosts/{original_ip}", response_class=HTMLResponse)
    async def ipam_update_host(request: Request, cidr: str, original_ip: str, hostname: str = Form(...), ip: str = Form(...), net_index: int = Form(0)):
        try:
            host = IpamHost(hostname=hostname.strip(), ip=ip.strip())
            ipam.update_host(cidr, original_ip, host)
        except KeyError:
            raise HTTPException(404, "Host not found")
        except (ValidationError, ValueError) as exc:
            try:
                network = ipam.get_network(cidr)
            except KeyError:
                raise HTTPException(404, "CIDR not found")
            response = templates.TemplateResponse(
                request,
                "partials/ipam_host_form.html",
                context(request, network=network, host=IpamHost(hostname=hostname.strip(), ip=ip.strip()), net_index=net_index, error=str(exc)),
                status_code=422,
            )
            return response
        return _render_full_accordion_body(request, cidr, net_index)

    @app.delete("/ipam/networks/{cidr:path}/hosts/{ip}", response_class=HTMLResponse)
    async def ipam_delete_host(request: Request, cidr: str, ip: str, net_index: int = 0):
        try:
            ipam.delete_host(cidr, ip)
        except KeyError:
            raise HTTPException(404, "Host not found")
        return _render_full_accordion_body(request, cidr, net_index)

    @app.get("/ipam/networks/{cidr:path}/hosts/{host_ip}/ports/new", response_class=HTMLResponse)
    async def ipam_port_new_form(request: Request, cidr: str, host_ip: str, net_index: int = 0):
        try:
            network = ipam.get_network(cidr)
        except KeyError:
            raise HTTPException(404, "CIDR not found")
        return templates.TemplateResponse(
            request,
            "partials/ipam_port_form.html",
            context(request, network=network, host_ip=host_ip, port=None, net_index=net_index),
        )

    @app.post("/ipam/networks/{cidr:path}/hosts/{host_ip}/ports", response_class=HTMLResponse)
    async def ipam_create_port(request: Request, cidr: str, host_ip: str, name: str = Form(...), port: int = Form(...), net_index: int = Form(0)):
        try:
            p = IpamPort(name=name.strip(), port=port)
            ipam.create_port(cidr, host_ip, p)
        except KeyError:
            raise HTTPException(404, "CIDR or host not found")
        except (ValidationError, ValueError) as exc:
            try:
                network = ipam.get_network(cidr)
            except KeyError:
                raise HTTPException(404, "CIDR not found")
            response = templates.TemplateResponse(
                request,
                "partials/ipam_port_form.html",
                context(request, network=network, host_ip=host_ip, port=None, net_index=net_index, error=str(exc)),
                status_code=422,
            )
            return response
        return _render_full_accordion_body(request, cidr, net_index)

    @app.put("/ipam/networks/{cidr:path}/hosts/{host_ip}/ports/{original_port:int}", response_class=HTMLResponse)
    async def ipam_update_port(
        request: Request, cidr: str, host_ip: str, original_port: int,
        name: str = Form(...), port: int = Form(...), net_index: int = Form(0)
    ):
        try:
            p = IpamPort(name=name.strip(), port=port)
            ipam.update_port(cidr, host_ip, original_port, p)
        except KeyError:
            raise HTTPException(404, "Port not found")
        except (ValidationError, ValueError) as exc:
            try:
                network = ipam.get_network(cidr)
            except KeyError:
                raise HTTPException(404, "CIDR not found")
            response = templates.TemplateResponse(
                request,
                "partials/ipam_port_form.html",
                context(request, network=network, host_ip=host_ip, port=None, net_index=net_index, error=str(exc)),
                status_code=422,
            )
            return response
        return _render_full_accordion_body(request, cidr, net_index)

    @app.delete("/ipam/networks/{cidr:path}/hosts/{host_ip}/ports/{port:int}", response_class=HTMLResponse)
    async def ipam_delete_port(request: Request, cidr: str, host_ip: str, port: int, net_index: int = 0):
        try:
            ipam.delete_port(cidr, host_ip, port)
        except KeyError:
            raise HTTPException(404, "Port not found")
        return _render_full_accordion_body(request, cidr, net_index)

    @app.put("/ipam/networks/{cidr:path}", response_class=HTMLResponse)
    async def ipam_update_network(request: Request, cidr: str, new_cidr: str = Form(..., alias="cidr")):
        try:
            network = IpamNetwork(cidr=new_cidr.strip())
            ipam.update_network(cidr, network)
        except KeyError:
            raise HTTPException(404, "CIDR not found")
        except (ValidationError, ValueError) as exc:
            response = templates.TemplateResponse(
                request,
                "partials/ipam_network_form.html",
                context(request, network=None, error=str(exc)),
                status_code=422,
            )
            response.headers["HX-Retarget"] = "#ipam-network-form-slot"
            return response
        return _render_network_list(request)

    @app.delete("/ipam/networks/{cidr:path}", response_class=HTMLResponse)
    async def ipam_delete_network(cidr: str):
        try:
            ipam.delete_network(cidr)
        except KeyError:
            raise HTTPException(404, "CIDR not found")
        return HTMLResponse("")

    def _render_full_accordion_body(request: Request, cidr: str, net_index: int = 0) -> HTMLResponse:
        try:
            network = ipam.get_network(cidr)
        except KeyError:
            raise HTTPException(404, "CIDR not found")
        return templates.TemplateResponse(
            request,
            "partials/ipam_network_body.html",
            context(request, network=network, net_index=net_index),
        )

    @app.get("/ipam/browse", response_class=HTMLResponse)
    async def ipam_browse_modal(request: Request):
        networks = ipam.list_networks()
        return templates.TemplateResponse(
            request, "partials/ipam_browse_modal.html", context(request, networks=networks)
        )

    return app


app = create_app()

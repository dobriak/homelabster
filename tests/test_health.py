import httpx
import pytest

from homelabster.health import HealthMonitor
from homelabster.models import Service


def service(health_url: str | None = "https://health.local") -> Service:
    return Service(id="test", name="Test", primary_url="https://test.local", fallback_url="http://10.0.0.1", health_url=health_url)


@pytest.mark.asyncio
async def test_health_statuses():
    monitor = HealthMonitor()
    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(204)))
    assert (await monitor.check(service(), client)).state == "healthy"
    await client.aclose()

    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(503)))
    assert (await monitor.check(service(), client)).state == "unhealthy"
    await client.aclose()

    assert (await monitor.check(service(None), httpx.AsyncClient())).state == "unknown"


@pytest.mark.asyncio
async def test_health_connection_failure_is_unhealthy():
    monitor = HealthMonitor()
    def fail(request: httpx.Request):
        raise httpx.ConnectError("no route", request=request)
    client = httpx.AsyncClient(transport=httpx.MockTransport(fail))
    status = await monitor.check(service(), client)
    await client.aclose()
    assert status.state == "unhealthy"
    assert status.checked_at is not None


@pytest.mark.asyncio
async def test_health_timeout_is_unhealthy():
    monitor = HealthMonitor()
    def fail(request: httpx.Request):
        raise httpx.ReadTimeout("slow", request=request)
    client = httpx.AsyncClient(transport=httpx.MockTransport(fail))
    status = await monitor.check(service(), client)
    await client.aclose()
    assert status.state == "unhealthy"
    assert status.detail == "Request timed out"

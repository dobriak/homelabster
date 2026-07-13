from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from .models import Service


@dataclass(frozen=True)
class HealthStatus:
    state: str = "unknown"
    detail: str = "Not checked yet"
    checked_at: datetime | None = None


class HealthMonitor:
    def __init__(self, timeout: float = 3, concurrency: int = 8):
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(concurrency)
        self.statuses: dict[str, HealthStatus] = {}

    async def check(self, service: Service, client: httpx.AsyncClient) -> HealthStatus:
        if not service.health_url:
            status = HealthStatus("unknown", "Health check is not configured")
            self.statuses[service.id] = status
            return status
        async with self.semaphore:
            try:
                response = await client.get(service.health_url, timeout=self.timeout, follow_redirects=True)
                if 200 <= response.status_code < 300:
                    status = HealthStatus("healthy", f"HTTP {response.status_code}", datetime.now(UTC))
                else:
                    status = HealthStatus("unhealthy", f"HTTP {response.status_code}", datetime.now(UTC))
            except httpx.TimeoutException:
                status = HealthStatus("unhealthy", "Request timed out", datetime.now(UTC))
            except httpx.HTTPError as exc:
                status = HealthStatus("unhealthy", type(exc).__name__, datetime.now(UTC))
        self.statuses[service.id] = status
        return status

    async def poll(self, services: list[Service]) -> None:
        async with httpx.AsyncClient() as client:
            await asyncio.gather(*(self.check(service, client) for service in services))

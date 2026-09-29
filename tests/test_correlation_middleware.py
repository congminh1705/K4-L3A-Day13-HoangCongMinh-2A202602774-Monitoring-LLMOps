from __future__ import annotations

import asyncio
import re

import httpx

from app.main import app


def _get_health(request_id: str | None = None) -> httpx.Response:
    async def send() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        headers = {"x-request-id": request_id} if request_id else None
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/health", headers=headers)

    return asyncio.run(send())


def test_generates_valid_request_id_and_response_time() -> None:
    response = _get_health()

    assert re.fullmatch(r"req-[0-9a-f]{8}", response.headers["x-request-id"])
    assert float(response.headers["x-response-time-ms"]) >= 0


def test_preserves_valid_request_id_and_replaces_invalid_one() -> None:
    supplied = _get_health("req-A1B2C3D4")
    invalid = _get_health("customer-data")

    assert supplied.headers["x-request-id"] == "req-a1b2c3d4"
    assert re.fullmatch(r"req-[0-9a-f]{8}", invalid.headers["x-request-id"])
    assert invalid.headers["x-request-id"] != "customer-data"

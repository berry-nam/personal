"""Test health check and app configuration."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_openapi_schema(client):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["info"]["title"] == "kr-acc"
    assert data["info"]["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_api_routes_registered(client):
    resp = await client.get("/openapi.json")
    paths = resp.json()["paths"]
    expected = [
        "/api/politicians",
        "/api/bills",
        "/api/votes",
        "/api/graph/co-sponsorship",
        "/api/parties",
        "/api/committees",
    ]
    for path in expected:
        assert path in paths, f"Missing route: {path}"

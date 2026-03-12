"""Integration tests for platform stats endpoint."""

from unittest.mock import patch


@patch("app.services.politician_service.get_platform_stats")
async def test_platform_stats(mock_stats, client):
    mock_stats.return_value = {
        "politicians": 300,
        "bills": 25000,
        "votes": 1500,
    }
    resp = await client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["politicians"] == 300
    assert data["bills"] == 25000
    assert data["votes"] == 1500

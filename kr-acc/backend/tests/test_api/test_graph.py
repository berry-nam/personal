"""Integration tests for graph API endpoints."""

from unittest.mock import patch


# ── Co-Sponsorship Network ────────────────────────────────────────────────────


@patch("app.services.graph_service.get_co_sponsorship_network")
async def test_co_sponsorship_network(mock_net, client):
    mock_net.return_value = {
        "nodes": [
            {"id": "A001", "name": "김철수", "party": "국민의힘", "group": "국민의힘"},
            {"id": "A002", "name": "이영희", "party": "더불어민주당", "group": "더불어민주당"},
        ],
        "edges": [
            {"source": "A001", "target": "A002", "weight": 5},
        ],
    }
    resp = await client.get("/api/graph/co-sponsorship")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert data["edges"][0]["weight"] == 5


@patch("app.services.graph_service.get_co_sponsorship_network")
async def test_co_sponsorship_with_filters(mock_net, client):
    mock_net.return_value = {"nodes": [], "edges": []}
    resp = await client.get("/api/graph/co-sponsorship?party=국민의힘&min_weight=5&limit=100")
    assert resp.status_code == 200
    kw = mock_net.call_args.kwargs
    assert kw["party"] == "국민의힘"
    assert kw["min_weight"] == 5
    assert kw["limit"] == 100


@patch("app.services.graph_service.get_co_sponsorship_network")
async def test_co_sponsorship_empty(mock_net, client):
    mock_net.return_value = {"nodes": [], "edges": []}
    resp = await client.get("/api/graph/co-sponsorship")
    assert resp.status_code == 200
    data = resp.json()
    assert data["nodes"] == []
    assert data["edges"] == []


# ── Neighbors ─────────────────────────────────────────────────────────────────


@patch("app.services.graph_service.get_neighbors")
async def test_get_neighbors(mock_neighbors, client):
    mock_neighbors.return_value = [
        {"assembly_id": "A002", "name": "이영희", "party": "더불어민주당", "weight": 10},
        {"assembly_id": "A003", "name": "박민수", "party": "국민의힘", "weight": 7},
    ]
    resp = await client.get("/api/graph/neighbors/A001")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["weight"] == 10
    assert data[0]["name"] == "이영희"


@patch("app.services.graph_service.get_neighbors")
async def test_get_neighbors_with_params(mock_neighbors, client):
    mock_neighbors.return_value = []
    resp = await client.get("/api/graph/neighbors/A001?min_weight=5&limit=10")
    assert resp.status_code == 200
    assert mock_neighbors.call_args.kwargs["min_weight"] == 5
    assert mock_neighbors.call_args.kwargs["limit"] == 10


@patch("app.services.graph_service.get_neighbors")
async def test_get_neighbors_empty(mock_neighbors, client):
    mock_neighbors.return_value = []
    resp = await client.get("/api/graph/neighbors/UNKNOWN")
    assert resp.status_code == 200
    assert resp.json() == []

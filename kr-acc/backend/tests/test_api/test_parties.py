"""Integration tests for party and committee reference endpoints."""

from unittest.mock import AsyncMock, MagicMock

from app.database import get_session
from app.main import app


def _mock_session_with_results(results):
    session = AsyncMock()
    mock_result = MagicMock()

    class FakeScalars:
        def all(self):
            return results

    mock_result.scalars.return_value = FakeScalars()
    session.execute.return_value = mock_result
    return session


class FakeParty:
    id = 1
    name = "국민의힘"
    color_hex = "#E61E2B"
    assembly_term = 22


class FakeCommittee:
    id = 1
    committee_id = "C001"
    name = "기획재정위원회"
    committee_type = "상임위원회"
    assembly_term = 22


# ── Parties ───────────────────────────────────────────────────────────────────


async def test_list_parties(client):
    session = _mock_session_with_results([FakeParty()])
    app.dependency_overrides[get_session] = lambda: session
    try:
        resp = await client.get("/api/parties")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "국민의힘"
        assert data[0]["color_hex"] == "#E61E2B"
    finally:
        app.dependency_overrides.clear()


async def test_list_parties_with_term(client):
    session = _mock_session_with_results([])
    app.dependency_overrides[get_session] = lambda: session
    try:
        resp = await client.get("/api/parties?assembly_term=21")
        assert resp.status_code == 200
        assert resp.json() == []
    finally:
        app.dependency_overrides.clear()


# ── Committees ────────────────────────────────────────────────────────────────


async def test_list_committees(client):
    session = _mock_session_with_results([FakeCommittee()])
    app.dependency_overrides[get_session] = lambda: session
    try:
        resp = await client.get("/api/committees")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "기획재정위원회"
        assert data[0]["committee_type"] == "상임위원회"
    finally:
        app.dependency_overrides.clear()


async def test_list_committees_with_term(client):
    session = _mock_session_with_results([])
    app.dependency_overrides[get_session] = lambda: session
    try:
        resp = await client.get("/api/committees?assembly_term=21")
        assert resp.status_code == 200
        assert resp.json() == []
    finally:
        app.dependency_overrides.clear()

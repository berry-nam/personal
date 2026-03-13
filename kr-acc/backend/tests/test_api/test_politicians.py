"""Integration tests for politician API endpoints."""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest


# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_politician(**overrides):
    """Create a mock Politician ORM object."""
    defaults = {
        "id": 1,
        "assembly_id": "ABC001",
        "name": "김철수",
        "name_hanja": "金哲洙",
        "party": "국민의힘",
        "constituency": "서울 강남구갑",
        "elected_count": 2,
        "committees": ["기획재정위원회"],
        "profile_url": None,
        "photo_url": "https://example.com/photo.jpg",
        "eng_name": "Kim Cheolsu",
        "bio": "서울대 법학과",
        "email": "kim@assembly.go.kr",
        "homepage": None,
        "office_address": "국회의원회관 301호",
        "birth_date": date(1980, 3, 15),
        "gender": "남",
        "assembly_term": 22,
    }
    defaults.update(overrides)

    class FakePol:
        pass

    pol = FakePol()
    for k, v in defaults.items():
        setattr(pol, k, v)
    return pol


def _make_bill(**overrides):
    """Create a mock Bill ORM object."""
    defaults = {
        "id": 1,
        "bill_id": "PRC_B001",
        "bill_no": "2400001",
        "bill_name": "테스트법안",
        "proposer_type": "의원",
        "propose_date": date(2024, 6, 1),
        "committee_id": "C001",
        "committee_name": "기획재정위원회",
        "status": "위원회 심사",
        "result": "원안가결",
        "assembly_term": 22,
        "detail_url": None,
        "sponsors": [],
    }
    defaults.update(overrides)

    class FakeBill:
        pass

    bill = FakeBill()
    for k, v in defaults.items():
        setattr(bill, k, v)
    return bill


# ── List Politicians ─────────────────────────────────────────────────────────


@patch("app.services.politician_service.list_politicians")
async def test_list_politicians_empty(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/politicians")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["pages"] == 0


@patch("app.services.politician_service.list_politicians")
async def test_list_politicians_with_results(mock_list, client):
    pol = _make_politician()
    mock_list.return_value = ([pol], 1)
    resp = await client.get("/api/politicians")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "김철수"
    assert data["items"][0]["party"] == "국민의힘"
    assert data["total"] == 1


@patch("app.services.politician_service.list_politicians")
async def test_list_politicians_pagination(mock_list, client):
    mock_list.return_value = ([], 50)
    resp = await client.get("/api/politicians?page=3&size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 3
    assert data["size"] == 10
    assert data["pages"] == 5
    # Verify service was called with correct params
    call_args = mock_list.call_args
    assert call_args.kwargs["page"] == 3
    assert call_args.kwargs["size"] == 10


@patch("app.services.politician_service.list_politicians")
async def test_list_politicians_filter_party(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/politicians?party=국민의힘")
    assert resp.status_code == 200
    call_args = mock_list.call_args
    assert call_args.kwargs["party"] == "국민의힘"


@patch("app.services.politician_service.list_politicians")
async def test_list_politicians_filter_name(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/politicians?name=김")
    assert resp.status_code == 200
    call_args = mock_list.call_args
    assert call_args.kwargs["name"] == "김"


@patch("app.services.politician_service.list_politicians")
async def test_list_politicians_filter_term(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/politicians?assembly_term=21")
    assert resp.status_code == 200
    call_args = mock_list.call_args
    assert call_args.kwargs["assembly_term"] == 21


async def test_list_politicians_invalid_page(client):
    resp = await client.get("/api/politicians?page=0")
    assert resp.status_code == 422


async def test_list_politicians_invalid_size(client):
    resp = await client.get("/api/politicians?size=200")
    assert resp.status_code == 422


# ── Get Politician ───────────────────────────────────────────────────────────


@patch("app.services.politician_service.get_politician_stats")
@patch("app.services.politician_service.get_politician")
async def test_get_politician_found(mock_get, mock_stats, client):
    mock_get.return_value = _make_politician()
    mock_stats.return_value = {
        "total_votes": 100,
        "yes_count": 80,
        "no_count": 10,
        "abstain_count": 5,
        "absent_count": 5,
        "participation_rate": 95.0,
        "bills_sponsored": 50,
        "bills_primary_sponsored": 10,
    }
    resp = await client.get("/api/politicians/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "김철수"
    assert data["assembly_id"] == "ABC001"
    assert data["stats"]["total_votes"] == 100
    assert data["stats"]["participation_rate"] == 95.0


@patch("app.services.politician_service.get_politician")
async def test_get_politician_not_found(mock_get, client):
    mock_get.return_value = None
    resp = await client.get("/api/politicians/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Politician not found"


# ── Politician Bills ─────────────────────────────────────────────────────────


@patch("app.services.bill_service.get_bills_by_politician")
@patch("app.services.politician_service.get_politician")
async def test_get_politician_bills(mock_get_pol, mock_get_bills, client):
    mock_get_pol.return_value = _make_politician()
    bill = _make_bill()
    mock_get_bills.return_value = ([bill], 1)

    resp = await client.get("/api/politicians/1/bills")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["bill_name"] == "테스트법안"
    assert data["total"] == 1


@patch("app.services.politician_service.get_politician")
async def test_get_politician_bills_not_found(mock_get, client):
    mock_get.return_value = None
    resp = await client.get("/api/politicians/9999/bills")
    assert resp.status_code == 404


@patch("app.services.bill_service.get_bills_by_politician")
@patch("app.services.politician_service.get_politician")
async def test_get_politician_bills_filter_sponsor_type(mock_get_pol, mock_bills, client):
    mock_get_pol.return_value = _make_politician()
    mock_bills.return_value = ([], 0)
    resp = await client.get("/api/politicians/1/bills?sponsor_type=primary")
    assert resp.status_code == 200
    call_args = mock_bills.call_args
    assert call_args.kwargs["sponsor_type"] == "primary"


# ── Politician Votes ─────────────────────────────────────────────────────────


@patch("app.services.vote_service.get_votes_by_politician")
@patch("app.services.politician_service.get_politician")
async def test_get_politician_votes(mock_get_pol, mock_get_votes, client):
    mock_get_pol.return_value = _make_politician()
    mock_get_votes.return_value = (
        [
            {
                "vote_id": "V001",
                "bill_id": "PRC_B001",
                "bill_name": "테스트법안",
                "vote_date": "2024-06-15",
                "vote_result": "찬성",
                "overall_result": "가결",
            }
        ],
        1,
    )

    resp = await client.get("/api/politicians/1/votes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["vote_result"] == "찬성"


@patch("app.services.politician_service.get_politician")
async def test_get_politician_votes_not_found(mock_get, client):
    mock_get.return_value = None
    resp = await client.get("/api/politicians/9999/votes")
    assert resp.status_code == 404


# ── Top Sponsors ─────────────────────────────────────────────────────────────


@patch("app.services.politician_service.get_top_sponsors")
async def test_top_sponsors(mock_top, client):
    mock_top.return_value = [
        {"id": 1, "name": "김철수", "party": "국민의힘", "photo_url": None, "bill_count": 42},
        {"id": 2, "name": "이영희", "party": "더불어민주당", "photo_url": None, "bill_count": 35},
    ]
    resp = await client.get("/api/politicians/top-sponsors")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["bill_count"] == 42


@patch("app.services.politician_service.get_top_sponsors")
async def test_top_sponsors_with_term(mock_top, client):
    mock_top.return_value = []
    resp = await client.get("/api/politicians/top-sponsors?assembly_term=21&limit=5")
    assert resp.status_code == 200
    call_args = mock_top.call_args
    assert call_args.kwargs["assembly_term"] == 21
    assert call_args.kwargs["limit"] == 5

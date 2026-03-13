"""Integration tests for vote API endpoints."""

from datetime import date
from unittest.mock import patch


def _make_vote(**overrides):
    """Create a mock Vote ORM object."""
    defaults = {
        "id": 1,
        "vote_id": "V001_20240615",
        "bill_id": "PRC_B001",
        "vote_date": date(2024, 6, 15),
        "total_members": 300,
        "yes_count": 200,
        "no_count": 50,
        "abstain_count": 10,
        "absent_count": 40,
        "result": "가결",
        "assembly_term": 22,
        "records": [],
    }
    defaults.update(overrides)

    class FakeVote:
        pass

    vote = FakeVote()
    for k, v in defaults.items():
        setattr(vote, k, v)
    return vote


def _make_vote_with_bill(**overrides):
    """Create a mock Vote with an attached bill."""
    vote = _make_vote(**overrides)

    class FakeBill:
        bill_name = "테스트법안"

    vote.bill = FakeBill()
    return vote


def _make_vote_record(politician_id=1, name="김철수", party="국민의힘", result="찬성"):
    class FakePol:
        pass

    class FakeRecord:
        pass

    pol = FakePol()
    pol.name = name
    pol.party = party

    rec = FakeRecord()
    rec.politician_id = politician_id
    rec.politician = pol
    rec.vote_result = result
    return rec


# ── List Votes ────────────────────────────────────────────────────────────────


@patch("app.services.vote_service.list_votes")
async def test_list_votes_empty(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/votes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@patch("app.services.vote_service.list_votes")
async def test_list_votes_with_results(mock_list, client):
    vote = _make_vote_with_bill()
    vote.bill_name = None  # VoteSummary gets bill_name from vote.bill fallback
    mock_list.return_value = ([vote], 1)
    resp = await client.get("/api/votes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["vote_id"] == "V001_20240615"
    assert data["items"][0]["yes_count"] == 200


@patch("app.services.vote_service.list_votes")
async def test_list_votes_filter_bill(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/votes?bill_id=PRC_B001")
    assert resp.status_code == 200
    assert mock_list.call_args.kwargs["bill_id"] == "PRC_B001"


@patch("app.services.vote_service.list_votes")
async def test_list_votes_filter_result(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/votes?result=가결")
    assert resp.status_code == 200
    assert mock_list.call_args.kwargs["result"] == "가결"


@patch("app.services.vote_service.list_votes")
async def test_list_votes_date_range(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/votes?date_from=2024-01-01&date_to=2024-12-31")
    assert resp.status_code == 200
    kw = mock_list.call_args.kwargs
    assert kw["date_from"] == date(2024, 1, 1)
    assert kw["date_to"] == date(2024, 12, 31)


@patch("app.services.vote_service.list_votes")
async def test_list_votes_pagination(mock_list, client):
    mock_list.return_value = ([], 60)
    resp = await client.get("/api/votes?page=2&size=20")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 2
    assert data["pages"] == 3


# ── Get Vote ──────────────────────────────────────────────────────────────────


@patch("app.services.vote_service.get_vote")
async def test_get_vote_found(mock_get, client):
    vote = _make_vote()
    vote.bill_name = "테스트법안"
    vote.records = [
        _make_vote_record(1, "김철수", "국민의힘", "찬성"),
        _make_vote_record(2, "이영희", "더불어민주당", "반대"),
    ]
    mock_get.return_value = vote

    resp = await client.get("/api/votes/V001_20240615")
    assert resp.status_code == 200
    data = resp.json()
    assert data["vote_id"] == "V001_20240615"
    assert len(data["records"]) == 2
    assert data["records"][0]["politician_name"] == "김철수"
    assert data["records"][0]["vote_result"] == "찬성"
    assert data["records"][1]["vote_result"] == "반대"


@patch("app.services.vote_service.get_vote")
async def test_get_vote_not_found(mock_get, client):
    mock_get.return_value = None
    resp = await client.get("/api/votes/NONEXISTENT")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Vote not found"

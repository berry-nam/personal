"""Integration tests for bill API endpoints."""

from datetime import date
from unittest.mock import patch


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


def _make_sponsor(politician_id=1, name="김철수", party="국민의힘", sponsor_type="primary"):
    class FakePol:
        pass

    class FakeSponsor:
        pass

    pol = FakePol()
    pol.name = name
    pol.party = party

    s = FakeSponsor()
    s.politician_id = politician_id
    s.politician = pol
    s.sponsor_type = sponsor_type
    return s


# ── List Bills ────────────────────────────────────────────────────────────────


@patch("app.services.bill_service.list_bills")
async def test_list_bills_empty(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/bills")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@patch("app.services.bill_service.list_bills")
async def test_list_bills_with_results(mock_list, client):
    mock_list.return_value = ([_make_bill()], 1)
    resp = await client.get("/api/bills")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["bill_name"] == "테스트법안"
    assert data["items"][0]["bill_id"] == "PRC_B001"


@patch("app.services.bill_service.list_bills")
async def test_list_bills_keyword_filter(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/bills?keyword=교육")
    assert resp.status_code == 200
    assert mock_list.call_args.kwargs["keyword"] == "교육"


@patch("app.services.bill_service.list_bills")
async def test_list_bills_date_filter(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/bills?date_from=2024-01-01&date_to=2024-12-31")
    assert resp.status_code == 200
    kw = mock_list.call_args.kwargs
    assert kw["date_from"] == date(2024, 1, 1)
    assert kw["date_to"] == date(2024, 12, 31)


@patch("app.services.bill_service.list_bills")
async def test_list_bills_pagination(mock_list, client):
    mock_list.return_value = ([], 100)
    resp = await client.get("/api/bills?page=5&size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 5
    assert data["pages"] == 10


@patch("app.services.bill_service.list_bills")
async def test_list_bills_filter_result(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/bills?result=원안가결")
    assert resp.status_code == 200
    assert mock_list.call_args.kwargs["result"] == "원안가결"


@patch("app.services.bill_service.list_bills")
async def test_list_bills_filter_assembly_term(mock_list, client):
    mock_list.return_value = ([], 0)
    resp = await client.get("/api/bills?assembly_term=21")
    assert resp.status_code == 200
    assert mock_list.call_args.kwargs["assembly_term"] == 21


# ── Get Bill ──────────────────────────────────────────────────────────────────


@patch("app.services.bill_service.get_bill")
async def test_get_bill_found(mock_get, client):
    bill = _make_bill()
    bill.sponsors = [_make_sponsor()]
    mock_get.return_value = bill

    resp = await client.get("/api/bills/PRC_B001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["bill_name"] == "테스트법안"
    assert len(data["sponsors"]) == 1
    assert data["sponsors"][0]["politician_name"] == "김철수"
    assert data["sponsors"][0]["sponsor_type"] == "primary"


@patch("app.services.bill_service.get_bill")
async def test_get_bill_not_found(mock_get, client):
    mock_get.return_value = None
    resp = await client.get("/api/bills/NONEXISTENT")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Bill not found"


# ── Bill Pipeline ─────────────────────────────────────────────────────────────


@patch("app.services.bill_service.get_pipeline_stats")
async def test_bill_pipeline(mock_pipeline, client):
    mock_pipeline.return_value = [
        {"result": "원안가결", "count": 50},
        {"result": "계류중", "count": 200},
        {"result": "폐기", "count": 30},
    ]
    resp = await client.get("/api/bills/pipeline")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert data[0]["result"] == "원안가결"


@patch("app.services.bill_service.get_pipeline_stats")
async def test_bill_pipeline_with_term(mock_pipeline, client):
    mock_pipeline.return_value = []
    resp = await client.get("/api/bills/pipeline?assembly_term=21")
    assert resp.status_code == 200
    assert mock_pipeline.call_args.kwargs["assembly_term"] == 21

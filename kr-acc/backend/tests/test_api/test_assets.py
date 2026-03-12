"""Integration tests for asset, company, and political fund endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession


def _mock_session_with_results(results):
    """Create a mock session that returns the given results from execute()."""
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()

    class FakeScalars:
        def all(self):
            return results

    mock_result.scalars.return_value = FakeScalars()
    mock_result.scalar_one_or_none.return_value = results[0] if results else None
    session.execute.return_value = mock_result
    return session


def _make_asset_declaration(
    id=1,
    politician_id=1,
    report_year=2023,
    total_assets=1_500_000_000,
    total_real_estate=800_000_000,
    total_deposits=400_000_000,
    total_securities=200_000_000,
    total_crypto=0,
    source="newstapa",
    items=None,
):
    class FakeDecl:
        pass

    d = FakeDecl()
    d.id = id
    d.politician_id = politician_id
    d.report_year = report_year
    d.total_assets = total_assets
    d.total_real_estate = total_real_estate
    d.total_deposits = total_deposits
    d.total_securities = total_securities
    d.total_crypto = total_crypto
    d.source = source
    d.items = items or []
    return d


def _make_fund(
    id=1,
    politician_id=1,
    fund_year=2023,
    fund_type="후원회",
    income_total=50_000_000,
    expense_total=30_000_000,
    balance=20_000_000,
    source="nec",
    items=None,
):
    class FakeFund:
        pass

    f = FakeFund()
    f.id = id
    f.politician_id = politician_id
    f.fund_year = fund_year
    f.fund_type = fund_type
    f.income_total = income_total
    f.expense_total = expense_total
    f.balance = balance
    f.source = source
    f.items = items or []
    return f


# ── Asset Declarations ────────────────────────────────────────────────────────


async def test_list_politician_assets(client):
    decl = _make_asset_declaration()
    session = _mock_session_with_results([decl])
    with patch("app.api.assets.get_session", return_value=session):
        from app.database import get_session
        from app.main import app

        app.dependency_overrides[get_session] = lambda: session
        try:
            resp = await client.get("/api/politicians/1/assets")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 1
            assert data[0]["report_year"] == 2023
            assert data[0]["total_assets"] == 1_500_000_000
        finally:
            app.dependency_overrides.clear()


async def test_get_politician_asset_detail(client):
    decl = _make_asset_declaration()
    session = _mock_session_with_results([decl])
    with patch("app.api.assets.get_session", return_value=session):
        from app.database import get_session
        from app.main import app

        app.dependency_overrides[get_session] = lambda: session
        try:
            resp = await client.get("/api/politicians/1/assets/2023")
            assert resp.status_code == 200
            data = resp.json()
            assert data["report_year"] == 2023
            assert data["source"] == "newstapa"
        finally:
            app.dependency_overrides.clear()


async def test_get_politician_asset_detail_not_found(client):
    session = _mock_session_with_results([])
    with patch("app.api.assets.get_session", return_value=session):
        from app.database import get_session
        from app.main import app

        app.dependency_overrides[get_session] = lambda: session
        try:
            resp = await client.get("/api/politicians/1/assets/2020")
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()


# ── Political Funds ───────────────────────────────────────────────────────────


async def test_list_politician_funds(client):
    fund = _make_fund()
    session = _mock_session_with_results([fund])
    from app.database import get_session
    from app.main import app

    app.dependency_overrides[get_session] = lambda: session
    try:
        resp = await client.get("/api/politicians/1/funds")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["fund_year"] == 2023
        assert data[0]["income_total"] == 50_000_000
    finally:
        app.dependency_overrides.clear()


# ── Companies ─────────────────────────────────────────────────────────────────


async def test_list_companies(client):
    class FakeCompany:
        id = 1
        corp_code = "00123456"
        corp_name = "삼성전자"
        stock_code = "005930"
        industry = "전기전자"

    session = _mock_session_with_results([FakeCompany()])
    from app.database import get_session
    from app.main import app

    app.dependency_overrides[get_session] = lambda: session
    try:
        resp = await client.get("/api/companies?name=삼성")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["corp_name"] == "삼성전자"
    finally:
        app.dependency_overrides.clear()

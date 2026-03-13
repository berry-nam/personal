"""Asset declaration & political fund API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import (
    AssetDeclaration,
    AssetItem,
    Company,
    Politician,
    PoliticalFund,
    PoliticianCompany,
)
from app.schemas.schemas import (
    AssetDeclarationOut,
    AssetSummaryOut,
    CompanyOut,
    PoliticalFundOut,
    PoliticalFundSummaryOut,
    PoliticianCompanyOut,
)

router = APIRouter(tags=["assets"])


@router.get("/assets/rankings")
async def asset_rankings(
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None, description="total, real_estate, deposits, securities, crypto"),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Top politicians by asset category (latest report year per politician)."""
    latest_year = (
        select(
            AssetDeclaration.politician_id,
            func.max(AssetDeclaration.report_year).label("max_year"),
        )
        .group_by(AssetDeclaration.politician_id)
        .subquery()
    )

    col_map = {
        "real_estate": AssetDeclaration.total_real_estate,
        "deposits": AssetDeclaration.total_deposits,
        "securities": AssetDeclaration.total_securities,
        "crypto": AssetDeclaration.total_crypto,
    }
    sort_col = col_map.get(category, AssetDeclaration.total_assets)

    result = await session.execute(
        select(
            Politician.id.label("politician_id"),
            Politician.name,
            Politician.party,
            Politician.photo_url,
            AssetDeclaration.total_assets,
            AssetDeclaration.total_real_estate,
            AssetDeclaration.total_deposits,
            AssetDeclaration.total_securities,
            AssetDeclaration.total_crypto,
            AssetDeclaration.report_year,
        )
        .join(AssetDeclaration, AssetDeclaration.politician_id == Politician.id)
        .join(
            latest_year,
            (latest_year.c.politician_id == AssetDeclaration.politician_id)
            & (latest_year.c.max_year == AssetDeclaration.report_year),
        )
        .where(sort_col.isnot(None), sort_col > 0)
        .order_by(sort_col.desc())
        .limit(limit)
    )
    return [
        {
            "politician_id": row.politician_id,
            "name": row.name,
            "party": row.party,
            "photo_url": row.photo_url,
            "total_assets": row.total_assets,
            "total_real_estate": row.total_real_estate,
            "total_deposits": row.total_deposits,
            "total_securities": row.total_securities,
            "total_crypto": row.total_crypto,
            "report_year": row.report_year,
        }
        for row in result.all()
    ]


@router.get("/assets/aggregate")
async def asset_aggregate(
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Aggregate asset categories by party (latest year per politician)."""
    latest_year = (
        select(
            AssetDeclaration.politician_id,
            func.max(AssetDeclaration.report_year).label("max_year"),
        )
        .group_by(AssetDeclaration.politician_id)
        .subquery()
    )

    result = await session.execute(
        select(
            Politician.party,
            func.sum(AssetDeclaration.total_assets).label("total_assets"),
            func.sum(AssetDeclaration.total_real_estate).label("total_real_estate"),
            func.sum(AssetDeclaration.total_deposits).label("total_deposits"),
            func.sum(AssetDeclaration.total_securities).label("total_securities"),
            func.sum(AssetDeclaration.total_crypto).label("total_crypto"),
            func.count(Politician.id).label("count"),
        )
        .join(AssetDeclaration, AssetDeclaration.politician_id == Politician.id)
        .join(
            latest_year,
            (latest_year.c.politician_id == AssetDeclaration.politician_id)
            & (latest_year.c.max_year == AssetDeclaration.report_year),
        )
        .group_by(Politician.party)
        .order_by(func.sum(AssetDeclaration.total_assets).desc())
    )
    return [
        {
            "party": row.party or "무소속",
            "total_assets": row.total_assets or 0,
            "total_real_estate": row.total_real_estate or 0,
            "total_deposits": row.total_deposits or 0,
            "total_securities": row.total_securities or 0,
            "total_crypto": row.total_crypto or 0,
            "count": row.count,
        }
        for row in result.all()
    ]


@router.get("/politicians/{politician_id}/assets", response_model=list[AssetSummaryOut])
async def list_politician_assets(
    politician_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get asset declaration summaries for a politician (yearly trend)."""
    result = await session.execute(
        select(AssetDeclaration)
        .where(AssetDeclaration.politician_id == politician_id)
        .order_by(AssetDeclaration.report_year.desc())
    )
    return [AssetSummaryOut.model_validate(r) for r in result.scalars().all()]


@router.get("/politicians/{politician_id}/assets/{year}", response_model=AssetDeclarationOut)
async def get_politician_asset_detail(
    politician_id: int,
    year: int,
    session: AsyncSession = Depends(get_session),
):
    """Get detailed asset declaration for a specific year."""
    result = await session.execute(
        select(AssetDeclaration)
        .options(selectinload(AssetDeclaration.items))
        .where(
            AssetDeclaration.politician_id == politician_id,
            AssetDeclaration.report_year == year,
        )
    )
    declaration = result.scalar_one_or_none()
    if not declaration:
        raise HTTPException(status_code=404, detail="Asset declaration not found")
    return AssetDeclarationOut.model_validate(declaration)


@router.get("/politicians/{politician_id}/companies", response_model=list[PoliticianCompanyOut])
async def list_politician_companies(
    politician_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get companies associated with a politician."""
    result = await session.execute(
        select(PoliticianCompany)
        .options(selectinload(PoliticianCompany.company))
        .where(PoliticianCompany.politician_id == politician_id)
        .order_by(PoliticianCompany.source_year.desc())
    )
    return [PoliticianCompanyOut.model_validate(r) for r in result.scalars().all()]


@router.get("/politicians/{politician_id}/funds", response_model=list[PoliticalFundSummaryOut])
async def list_politician_funds(
    politician_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get political fund summaries for a politician."""
    result = await session.execute(
        select(PoliticalFund)
        .where(PoliticalFund.politician_id == politician_id)
        .order_by(PoliticalFund.fund_year.desc())
    )
    return [PoliticalFundSummaryOut.model_validate(r) for r in result.scalars().all()]


@router.get("/politicians/{politician_id}/funds/{year}", response_model=list[PoliticalFundOut])
async def get_politician_fund_detail(
    politician_id: int,
    year: int,
    session: AsyncSession = Depends(get_session),
):
    """Get detailed political fund data for a specific year."""
    result = await session.execute(
        select(PoliticalFund)
        .options(selectinload(PoliticalFund.items))
        .where(
            PoliticalFund.politician_id == politician_id,
            PoliticalFund.fund_year == year,
        )
    )
    return [PoliticalFundOut.model_validate(r) for r in result.scalars().all()]


@router.get("/companies", response_model=list[CompanyOut])
async def list_companies(
    name: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Search companies by name."""
    query = select(Company)
    if name:
        query = query.where(Company.corp_name.ilike(f"%{name}%"))
    query = query.limit(50)
    result = await session.execute(query)
    return [CompanyOut.model_validate(r) for r in result.scalars().all()]


# ── Aggregate asset item endpoints ─────────────────────────────────────────


@router.get("/assets/items/stocks")
async def top_stock_holdings(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Top stock/securities holdings across all politicians."""
    result = await session.execute(
        select(
            AssetItem.description,
            AssetItem.subcategory,
            AssetItem.relation,
            AssetItem.value_krw,
            Politician.id.label("politician_id"),
            Politician.name,
            Politician.party,
            Politician.photo_url,
        )
        .join(AssetDeclaration, AssetDeclaration.id == AssetItem.declaration_id)
        .join(Politician, Politician.id == AssetDeclaration.politician_id)
        .where(AssetItem.category == "securities", AssetItem.value_krw.isnot(None))
        .order_by(AssetItem.value_krw.desc())
        .limit(limit)
    )
    return [
        {
            "description": row.description,
            "subcategory": row.subcategory,
            "relation": row.relation,
            "value_krw": row.value_krw,
            "politician_id": row.politician_id,
            "name": row.name,
            "party": row.party,
            "photo_url": row.photo_url,
        }
        for row in result.all()
    ]


@router.get("/assets/items/real-estate")
async def top_real_estate(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Top real estate holdings across all politicians."""
    result = await session.execute(
        select(
            AssetItem.description,
            AssetItem.subcategory,
            AssetItem.relation,
            AssetItem.value_krw,
            Politician.id.label("politician_id"),
            Politician.name,
            Politician.party,
            Politician.photo_url,
        )
        .join(AssetDeclaration, AssetDeclaration.id == AssetItem.declaration_id)
        .join(Politician, Politician.id == AssetDeclaration.politician_id)
        .where(AssetItem.category == "real_estate", AssetItem.value_krw.isnot(None))
        .order_by(AssetItem.value_krw.desc())
        .limit(limit)
    )
    return [
        {
            "description": row.description,
            "subcategory": row.subcategory,
            "relation": row.relation,
            "value_krw": row.value_krw,
            "politician_id": row.politician_id,
            "name": row.name,
            "party": row.party,
            "photo_url": row.photo_url,
        }
        for row in result.all()
    ]


@router.get("/assets/items/crypto")
async def top_crypto_holdings(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Top crypto holdings across all politicians."""
    result = await session.execute(
        select(
            AssetItem.description,
            AssetItem.subcategory,
            AssetItem.relation,
            AssetItem.value_krw,
            Politician.id.label("politician_id"),
            Politician.name,
            Politician.party,
            Politician.photo_url,
        )
        .join(AssetDeclaration, AssetDeclaration.id == AssetItem.declaration_id)
        .join(Politician, Politician.id == AssetDeclaration.politician_id)
        .where(AssetItem.category == "crypto", AssetItem.value_krw.isnot(None))
        .order_by(AssetItem.value_krw.desc())
        .limit(limit)
    )
    return [
        {
            "description": row.description,
            "subcategory": row.subcategory,
            "relation": row.relation,
            "value_krw": row.value_krw,
            "politician_id": row.politician_id,
            "name": row.name,
            "party": row.party,
            "photo_url": row.photo_url,
        }
        for row in result.all()
    ]


@router.get("/assets/items/all")
async def all_asset_items(
    category: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """All asset items with politician info, optionally filtered by category."""
    query = (
        select(
            AssetItem.category,
            AssetItem.subcategory,
            AssetItem.description,
            AssetItem.relation,
            AssetItem.value_krw,
            AssetItem.change_krw,
            AssetItem.note,
            Politician.id.label("politician_id"),
            Politician.name,
            Politician.party,
        )
        .join(AssetDeclaration, AssetDeclaration.id == AssetItem.declaration_id)
        .join(Politician, Politician.id == AssetDeclaration.politician_id)
    )
    if category:
        query = query.where(AssetItem.category == category)
    query = query.order_by(AssetItem.value_krw.desc()).limit(limit)
    result = await session.execute(query)
    return [
        {
            "category": row.category,
            "subcategory": row.subcategory,
            "description": row.description,
            "relation": row.relation,
            "value_krw": row.value_krw,
            "change_krw": row.change_krw,
            "note": row.note,
            "politician_id": row.politician_id,
            "name": row.name,
            "party": row.party,
        }
        for row in result.all()
    ]


@router.get("/funds/rankings")
async def fund_rankings(
    year: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Politicians ranked by political fund income."""
    query = (
        select(
            PoliticalFund.fund_year,
            PoliticalFund.income_total,
            PoliticalFund.expense_total,
            PoliticalFund.balance,
            Politician.id.label("politician_id"),
            Politician.name,
            Politician.party,
            Politician.photo_url,
        )
        .join(Politician, Politician.id == PoliticalFund.politician_id)
    )
    if year:
        query = query.where(PoliticalFund.fund_year == year)
    else:
        # Latest year per politician
        latest = (
            select(
                PoliticalFund.politician_id,
                func.max(PoliticalFund.fund_year).label("max_year"),
            )
            .group_by(PoliticalFund.politician_id)
            .subquery()
        )
        query = query.join(
            latest,
            (latest.c.politician_id == PoliticalFund.politician_id)
            & (latest.c.max_year == PoliticalFund.fund_year),
        )
    result = await session.execute(
        query.order_by(PoliticalFund.income_total.desc()).limit(limit)
    )
    return [
        {
            "politician_id": row.politician_id,
            "name": row.name,
            "party": row.party,
            "photo_url": row.photo_url,
            "fund_year": row.fund_year,
            "income_total": row.income_total,
            "expense_total": row.expense_total,
            "balance": row.balance,
        }
        for row in result.all()
    ]


@router.get("/assets/companies/all")
async def all_company_holdings(
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """All politician-company relationships with details."""
    result = await session.execute(
        select(
            PoliticianCompany.relation_type,
            PoliticianCompany.value_krw,
            PoliticianCompany.source_year,
            Company.corp_name,
            Company.industry,
            Company.stock_code,
            Politician.id.label("politician_id"),
            Politician.name,
            Politician.party,
            Politician.photo_url,
        )
        .join(Company, Company.id == PoliticianCompany.company_id)
        .join(Politician, Politician.id == PoliticianCompany.politician_id)
        .order_by(PoliticianCompany.value_krw.desc().nullslast())
    )
    return [
        {
            "relation_type": row.relation_type,
            "value_krw": row.value_krw,
            "source_year": row.source_year,
            "corp_name": row.corp_name,
            "industry": row.industry,
            "stock_code": row.stock_code,
            "politician_id": row.politician_id,
            "name": row.name,
            "party": row.party,
            "photo_url": row.photo_url,
        }
        for row in result.all()
    ]

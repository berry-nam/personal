"""Asset declaration & political fund API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import (
    AssetDeclaration,
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
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Top politicians by total assets (latest report year per politician)."""
    # Subquery: latest report year per politician
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
            Politician.id.label("politician_id"),
            Politician.name,
            Politician.party,
            Politician.photo_url,
            AssetDeclaration.total_assets,
            AssetDeclaration.report_year,
        )
        .join(AssetDeclaration, AssetDeclaration.politician_id == Politician.id)
        .join(
            latest_year,
            (latest_year.c.politician_id == AssetDeclaration.politician_id)
            & (latest_year.c.max_year == AssetDeclaration.report_year),
        )
        .where(AssetDeclaration.total_assets.isnot(None))
        .order_by(AssetDeclaration.total_assets.desc())
        .limit(limit)
    )
    return [
        {
            "politician_id": row.politician_id,
            "name": row.name,
            "party": row.party,
            "photo_url": row.photo_url,
            "total_assets": row.total_assets,
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

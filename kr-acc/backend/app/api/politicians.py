"""Politician API endpoints."""

import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.schemas import (
    PaginatedResponse,
    PoliticianDetail,
    PoliticianDetailWithStats,
    PoliticianStats,
    PoliticianSummary,
)
from app.services import bill_service, politician_service, vote_service

router = APIRouter(prefix="/politicians", tags=["politicians"])


@router.get("", response_model=PaginatedResponse)
async def list_politicians(
    party: str | None = None,
    name: str | None = None,
    assembly_term: int | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """List politicians with optional filtering by party or name."""
    politicians, total = await politician_service.list_politicians(
        session, party=party, name=name, assembly_term=assembly_term, page=page, size=size
    )
    return PaginatedResponse(
        items=[PoliticianSummary.model_validate(p) for p in politicians],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


@router.get("/{politician_id}", response_model=PoliticianDetailWithStats)
async def get_politician(
    politician_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single politician with vote/sponsorship stats."""
    pol = await politician_service.get_politician(session, politician_id)
    if not pol:
        raise HTTPException(status_code=404, detail="Politician not found")

    stats_data = await politician_service.get_politician_stats(session, politician_id)
    result = PoliticianDetailWithStats.model_validate(pol)
    result.stats = PoliticianStats(**stats_data)
    return result


@router.get("/{politician_id}/bills", response_model=PaginatedResponse)
async def get_politician_bills(
    politician_id: int,
    sponsor_type: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Get bills sponsored by a politician."""
    pol = await politician_service.get_politician(session, politician_id)
    if not pol:
        raise HTTPException(status_code=404, detail="Politician not found")

    from app.schemas.schemas import BillSummary

    bills, total = await bill_service.get_bills_by_politician(
        session, politician_id, sponsor_type=sponsor_type, page=page, size=size
    )
    return PaginatedResponse(
        items=[BillSummary.model_validate(b) for b in bills],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


@router.get("/{politician_id}/votes", response_model=PaginatedResponse)
async def get_politician_votes(
    politician_id: int,
    vote_result: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Get vote records for a politician."""
    pol = await politician_service.get_politician(session, politician_id)
    if not pol:
        raise HTTPException(status_code=404, detail="Politician not found")

    votes, total = await vote_service.get_votes_by_politician(
        session, politician_id, vote_result=vote_result, page=page, size=size
    )
    return PaginatedResponse(
        items=votes,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )

"""Bill API endpoints."""

import math
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.schemas import BillDetail, BillSponsorOut, BillSummary, PaginatedResponse
from app.services import bill_service

router = APIRouter(prefix="/bills", tags=["bills"])


@router.get("", response_model=PaginatedResponse)
async def list_bills(
    keyword: str | None = None,
    proposer_type: str | None = None,
    committee_name: str | None = None,
    result: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    assembly_term: int = 22,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """List bills with filtering and pagination."""
    bills, total = await bill_service.list_bills(
        session,
        keyword=keyword,
        proposer_type=proposer_type,
        committee_name=committee_name,
        result=result,
        date_from=date_from,
        date_to=date_to,
        assembly_term=assembly_term,
        page=page,
        size=size,
    )
    return PaginatedResponse(
        items=[BillSummary.model_validate(b) for b in bills],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


@router.get("/{bill_id}", response_model=BillDetail)
async def get_bill(
    bill_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get a single bill with sponsor details."""
    bill = await bill_service.get_bill(session, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    sponsors = [
        BillSponsorOut(
            politician_id=s.politician_id,
            politician_name=s.politician.name if s.politician else None,
            politician_party=s.politician.party if s.politician else None,
            sponsor_type=s.sponsor_type,
        )
        for s in bill.sponsors
    ]

    detail = BillDetail.model_validate(bill)
    detail.sponsors = sponsors
    return detail

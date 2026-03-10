"""Vote API endpoints."""

import math
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.schemas import PaginatedResponse, VoteDetail, VoteRecordOut, VoteSummary
from app.services import vote_service

router = APIRouter(prefix="/votes", tags=["votes"])


@router.get("", response_model=PaginatedResponse)
async def list_votes(
    bill_id: str | None = None,
    result: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    assembly_term: int = 22,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """List votes with filtering and pagination."""
    votes, total = await vote_service.list_votes(
        session,
        bill_id=bill_id,
        result=result,
        date_from=date_from,
        date_to=date_to,
        assembly_term=assembly_term,
        page=page,
        size=size,
    )
    items = []
    for v in votes:
        item = VoteSummary.model_validate(v)
        items.append(item)

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


@router.get("/{vote_id}", response_model=VoteDetail)
async def get_vote(
    vote_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get a single vote with per-member breakdown."""
    vote = await vote_service.get_vote(session, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")

    records = [
        VoteRecordOut(
            politician_id=r.politician_id,
            politician_name=r.politician.name if r.politician else None,
            politician_party=r.politician.party if r.politician else None,
            vote_result=r.vote_result,
        )
        for r in vote.records
    ]

    detail = VoteDetail.model_validate(vote)
    detail.records = records
    return detail

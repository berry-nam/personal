"""Stats API endpoints — overview statistics and pipeline data."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Bill, BillSponsor, Politician, Vote, VoteRecord

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
async def get_overview(
    assembly_term: int = 22,
    session: AsyncSession = Depends(get_session),
):
    """Get summary statistics for the dashboard."""
    politicians_count = (
        await session.execute(
            select(func.count(Politician.id)).where(
                Politician.assembly_term == assembly_term
            )
        )
    ).scalar_one()

    bills_count = (
        await session.execute(
            select(func.count(Bill.id)).where(Bill.assembly_term == assembly_term)
        )
    ).scalar_one()

    votes_count = (
        await session.execute(
            select(func.count(Vote.id)).where(Vote.assembly_term == assembly_term)
        )
    ).scalar_one()

    # Party distribution with member counts
    party_rows = (
        await session.execute(
            select(Politician.party, func.count(Politician.id))
            .where(Politician.assembly_term == assembly_term)
            .group_by(Politician.party)
            .order_by(func.count(Politician.id).desc())
        )
    ).all()

    parties = [
        {"party": row[0] or "무소속", "count": row[1]} for row in party_rows
    ]

    return {
        "politicians": politicians_count,
        "bills": bills_count,
        "votes": votes_count,
        "parties": parties,
    }

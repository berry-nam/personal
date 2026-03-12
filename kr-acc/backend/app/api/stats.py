"""Statistics API endpoints for dashboard visualizations."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Bill, Politician, Vote

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/party-seats")
async def party_seats(
    assembly_term: int = Query(22),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Party seat counts with color codes for waffle chart."""
    result = await session.execute(
        select(
            Politician.party,
            func.count(Politician.id).label("count"),
        )
        .where(Politician.assembly_term == assembly_term)
        .group_by(Politician.party)
        .order_by(func.count(Politician.id).desc())
    )
    from app.models import Party

    # Fetch party colors
    party_colors = {}
    color_result = await session.execute(
        select(Party.name, Party.color_hex).where(Party.assembly_term == assembly_term)
    )
    for row in color_result.all():
        party_colors[row.name] = row.color_hex

    return [
        {
            "party": row.party or "무소속",
            "count": row.count,
            "color_hex": party_colors.get(row.party) or "#9CA3AF",
        }
        for row in result.all()
    ]


@router.get("/demographics")
async def demographics(
    assembly_term: int = Query(22),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Gender and age bracket demographics."""
    # Gender counts
    gender_result = await session.execute(
        select(
            Politician.gender,
            func.count(Politician.id).label("count"),
        )
        .where(Politician.assembly_term == assembly_term)
        .group_by(Politician.gender)
    )
    gender = [
        {"gender": row.gender or "미상", "count": row.count}
        for row in gender_result.all()
    ]

    # Age brackets from birth_date
    age_expr = func.date_part("year", func.age(Politician.birth_date))
    bracket_expr = case(
        (age_expr < 40, "30대"),
        (age_expr < 50, "40대"),
        (age_expr < 60, "50대"),
        (age_expr < 70, "60대"),
        else_="70대+",
    )
    age_result = await session.execute(
        select(
            bracket_expr.label("bracket"),
            func.count(Politician.id).label("count"),
        )
        .where(
            Politician.assembly_term == assembly_term,
            Politician.birth_date.isnot(None),
        )
        .group_by(bracket_expr)
        .order_by(bracket_expr)
    )
    age_brackets = [
        {"bracket": row.bracket, "count": row.count}
        for row in age_result.all()
    ]

    return {"gender": gender, "age_brackets": age_brackets}


@router.get("/vote-participation")
async def vote_participation(
    assembly_term: int = Query(22),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Average vote participation rate across all plenary votes."""
    result = await session.execute(
        select(
            func.avg(
                (Vote.total_members - Vote.absent_count).cast(float)
                / Vote.total_members
                * 100
            ).label("avg_participation"),
            func.count(Vote.id).label("total_votes"),
        ).where(
            Vote.assembly_term == assembly_term,
            Vote.total_members > 0,
        )
    )
    row = result.one()
    return {
        "avg_participation": round(row.avg_participation or 0, 1),
        "total_votes": row.total_votes or 0,
    }


@router.get("/bill-trend")
async def bill_trend(
    assembly_term: int = Query(22),
    weeks: int = Query(12, ge=1, le=52),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Weekly bill proposal counts for sparkline chart."""
    result = await session.execute(
        select(
            func.date_trunc("week", Bill.propose_date).label("week"),
            func.count(Bill.id).label("count"),
        )
        .where(
            Bill.assembly_term == assembly_term,
            Bill.propose_date.isnot(None),
        )
        .group_by(text("1"))
        .order_by(text("1 DESC"))
        .limit(weeks)
    )
    rows = result.all()
    return [
        {"week": row.week.isoformat() if row.week else None, "count": row.count}
        for row in reversed(rows)
    ]

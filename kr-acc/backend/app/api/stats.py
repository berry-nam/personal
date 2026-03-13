"""Statistics API endpoints for dashboard visualizations."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Float, case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Bill, Politician, Vote

router = APIRouter(prefix="/stats", tags=["stats"])

# Map constituency prefixes to regions for the Korea map
_REGION_MAP = {
    "서울": "서울",
    "부산": "부산",
    "대구": "대구",
    "인천": "인천",
    "광주": "광주",
    "대전": "대전",
    "울산": "울산",
    "세종": "세종",
    "경기": "경기",
    "강원": "강원",
    "충북": "충북",
    "충남": "충남",
    "전북": "전북",
    "전남": "전남",
    "경북": "경북",
    "경남": "경남",
    "제주": "제주",
}


def _constituency_to_region(constituency: str | None) -> str:
    if not constituency:
        return "비례대표"
    for prefix, region in _REGION_MAP.items():
        if constituency.startswith(prefix):
            return region
    return "비례대표"


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


@router.get("/region-seats")
async def region_seats(
    assembly_term: int = Query(22),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Politician counts by region (derived from constituency) for Korea map."""
    result = await session.execute(
        select(Politician.constituency, Politician.party).where(
            Politician.assembly_term == assembly_term,
        )
    )
    region_data: dict[str, dict[str, int]] = {}
    for row in result.all():
        region = _constituency_to_region(row.constituency)
        if region not in region_data:
            region_data[region] = {}
        party = row.party or "무소속"
        region_data[region][party] = region_data[region].get(party, 0) + 1

    return [
        {
            "region": region,
            "total": sum(parties.values()),
            "parties": parties,
        }
        for region, parties in sorted(region_data.items(), key=lambda x: -sum(x[1].values()))
    ]


@router.get("/controversial-votes")
async def controversial_votes(
    assembly_term: int = Query(22),
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Votes with highest opposition rate — most controversial decisions."""
    result = await session.execute(
        select(
            Vote.id,
            Vote.vote_id,
            Vote.bill_id,
            Vote.vote_date,
            Vote.total_members,
            Vote.yes_count,
            Vote.no_count,
            Vote.abstain_count,
            Vote.absent_count,
            Vote.result,
            Bill.bill_name,
        )
        .join(Bill, Bill.bill_id == Vote.bill_id)
        .where(
            Vote.assembly_term == assembly_term,
            Vote.total_members > 0,
            Vote.no_count > 0,
        )
        .order_by((Vote.no_count.cast(Float) / Vote.total_members).desc())
        .limit(limit)
    )
    return [
        {
            "vote_id": row.vote_id,
            "bill_name": row.bill_name,
            "vote_date": row.vote_date.isoformat() if row.vote_date else None,
            "total_members": row.total_members,
            "yes_count": row.yes_count,
            "no_count": row.no_count,
            "abstain_count": row.abstain_count,
            "absent_count": row.absent_count,
            "result": row.result,
            "opposition_rate": round(
                (row.no_count / row.total_members * 100) if row.total_members else 0, 1
            ),
        }
        for row in result.all()
    ]


@router.get("/absentee-ranking")
async def absentee_ranking(
    assembly_term: int = Query(22),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Politicians ranked by highest absence rate in votes."""
    from app.models import VoteRecord

    total_votes_sub = (
        select(func.count(Vote.id).label("cnt"))
        .where(Vote.assembly_term == assembly_term)
        .scalar_subquery()
    )

    result = await session.execute(
        select(
            Politician.id.label("politician_id"),
            Politician.name,
            Politician.party,
            Politician.photo_url,
            func.count(VoteRecord.id).label("total_votes"),
            func.count(VoteRecord.id)
            .filter(VoteRecord.vote_result == "불참")
            .label("absent_count"),
        )
        .join(VoteRecord, VoteRecord.politician_id == Politician.id)
        .where(Politician.assembly_term == assembly_term)
        .group_by(Politician.id, Politician.name, Politician.party, Politician.photo_url)
        .having(func.count(VoteRecord.id) > 0)
        .order_by(
            (
                func.count(VoteRecord.id).filter(VoteRecord.vote_result == "불참").cast(Float)
                / func.count(VoteRecord.id)
            ).desc()
        )
        .limit(limit)
    )
    return [
        {
            "politician_id": row.politician_id,
            "name": row.name,
            "party": row.party,
            "photo_url": row.photo_url,
            "total_votes": row.total_votes,
            "absent_count": row.absent_count,
            "absence_rate": round(
                (row.absent_count / row.total_votes * 100) if row.total_votes else 0, 1
            ),
        }
        for row in result.all()
    ]

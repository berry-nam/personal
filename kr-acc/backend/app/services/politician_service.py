"""Politician query service."""

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Bill, BillSponsor, Politician, Vote, VoteRecord


async def list_politicians(
    session: AsyncSession,
    *,
    party: str | None = None,
    name: str | None = None,
    assembly_term: int | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Politician], int]:
    """List politicians with optional filters.

    Returns:
        Tuple of (politician list, total count).
    """
    query = select(Politician)
    count_query = select(func.count(Politician.id))

    if assembly_term is not None:
        query = query.where(Politician.assembly_term == assembly_term)
        count_query = count_query.where(Politician.assembly_term == assembly_term)

    if party:
        query = query.where(Politician.party == party)
        count_query = count_query.where(Politician.party == party)
    if name:
        query = query.where(Politician.name.ilike(f"%{name}%"))
        count_query = count_query.where(Politician.name.ilike(f"%{name}%"))

    total = (await session.execute(count_query)).scalar_one()
    query = query.order_by(Politician.name).offset((page - 1) * size).limit(size)
    result = await session.execute(query)
    return list(result.scalars().all()), total


async def get_politician(session: AsyncSession, politician_id: int) -> Politician | None:
    """Get a single politician by DB ID."""
    return await session.get(Politician, politician_id)


async def get_politician_by_assembly_id(
    session: AsyncSession, assembly_id: str
) -> Politician | None:
    """Get a single politician by assembly ID."""
    result = await session.execute(
        select(Politician).where(Politician.assembly_id == assembly_id)
    )
    return result.scalar_one_or_none()


async def get_politician_stats(session: AsyncSession, politician_id: int) -> dict:
    """Compute vote and sponsorship stats for a politician."""
    # Vote stats
    vote_result = await session.execute(
        select(
            func.count(VoteRecord.id).label("total"),
            func.count(VoteRecord.id).filter(VoteRecord.vote_result == "찬성").label("yes"),
            func.count(VoteRecord.id).filter(VoteRecord.vote_result == "반대").label("no"),
            func.count(VoteRecord.id).filter(VoteRecord.vote_result == "기권").label("abstain"),
            func.count(VoteRecord.id).filter(VoteRecord.vote_result == "불참").label("absent"),
        ).where(VoteRecord.politician_id == politician_id)
    )
    row = vote_result.one()
    total = row.total or 0
    participation = ((total - (row.absent or 0)) / total * 100) if total > 0 else 0.0

    # Sponsorship stats
    sponsor_result = await session.execute(
        select(
            func.count(BillSponsor.id).label("total_sponsored"),
            func.count(BillSponsor.id)
            .filter(BillSponsor.sponsor_type == "primary")
            .label("primary_sponsored"),
        ).where(BillSponsor.politician_id == politician_id)
    )
    srow = sponsor_result.one()

    return {
        "total_votes": total,
        "yes_count": row.yes or 0,
        "no_count": row.no or 0,
        "abstain_count": row.abstain or 0,
        "absent_count": row.absent or 0,
        "participation_rate": round(participation, 1),
        "bills_sponsored": srow.total_sponsored or 0,
        "bills_primary_sponsored": srow.primary_sponsored or 0,
    }


async def get_top_sponsors(
    session: AsyncSession,
    *,
    assembly_term: int | None = None,
    limit: int = 10,
) -> list[dict]:
    """Get politicians ranked by number of primary-sponsored bills.

    Returns:
        List of dicts with politician info and bill count.
    """
    query = (
        select(
            Politician.id,
            Politician.name,
            Politician.party,
            Politician.photo_url,
            func.count(BillSponsor.id).label("bill_count"),
        )
        .join(BillSponsor, BillSponsor.politician_id == Politician.id)
        .where(BillSponsor.sponsor_type == "primary")
    )
    if assembly_term is not None:
        query = query.where(Politician.assembly_term == assembly_term)
    query = (
        query.group_by(Politician.id, Politician.name, Politician.party, Politician.photo_url)
        .order_by(desc("bill_count"))
        .limit(limit)
    )
    result = await session.execute(query)
    return [
        {
            "id": row.id,
            "name": row.name,
            "party": row.party,
            "photo_url": row.photo_url,
            "bill_count": row.bill_count,
        }
        for row in result.all()
    ]


async def get_platform_stats(session: AsyncSession) -> dict:
    """Get overall platform statistics."""
    pol_count = (await session.execute(select(func.count(Politician.id)))).scalar_one()
    bill_count = (await session.execute(select(func.count(Bill.id)))).scalar_one()
    vote_count = (await session.execute(select(func.count(Vote.id)))).scalar_one()
    return {
        "politicians": pol_count,
        "bills": bill_count,
        "votes": vote_count,
    }

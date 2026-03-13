"""Vote query service."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Bill, Vote, VoteRecord


async def list_votes(
    session: AsyncSession,
    *,
    bill_id: str | None = None,
    result: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    assembly_term: int | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Vote], int]:
    """List votes with filtering and pagination."""
    query = select(Vote)
    count_query = select(func.count(Vote.id))

    if assembly_term is not None:
        query = query.where(Vote.assembly_term == assembly_term)
        count_query = count_query.where(Vote.assembly_term == assembly_term)

    if bill_id:
        query = query.where(Vote.bill_id == bill_id)
        count_query = count_query.where(Vote.bill_id == bill_id)
    if result:
        query = query.where(Vote.result == result)
        count_query = count_query.where(Vote.result == result)
    if date_from:
        query = query.where(Vote.vote_date >= date_from)
        count_query = count_query.where(Vote.vote_date >= date_from)
    if date_to:
        query = query.where(Vote.vote_date <= date_to)
        count_query = count_query.where(Vote.vote_date <= date_to)

    total = (await session.execute(count_query)).scalar_one()
    query = (
        query.options(selectinload(Vote.bill))
        .order_by(Vote.vote_date.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    rows = await session.execute(query)
    return list(rows.scalars().all()), total


async def get_vote(session: AsyncSession, vote_id: str) -> Vote | None:
    """Get a single vote with per-member records eagerly loaded."""
    result = await session.execute(
        select(Vote)
        .where(Vote.vote_id == vote_id)
        .options(selectinload(Vote.records).selectinload(VoteRecord.politician))
    )
    return result.scalar_one_or_none()


async def get_votes_by_politician(
    session: AsyncSession,
    politician_id: int,
    *,
    vote_result: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[dict], int]:
    """Get vote records for a politician with bill info."""
    base = (
        select(VoteRecord, Vote, Bill)
        .join(Vote, VoteRecord.vote_id == Vote.vote_id)
        .join(Bill, Vote.bill_id == Bill.bill_id)
        .where(VoteRecord.politician_id == politician_id)
    )
    count_base = (
        select(func.count(VoteRecord.id))
        .join(Vote, VoteRecord.vote_id == Vote.vote_id)
        .where(VoteRecord.politician_id == politician_id)
    )

    if vote_result:
        base = base.where(VoteRecord.vote_result == vote_result)
        count_base = count_base.where(VoteRecord.vote_result == vote_result)

    total = (await session.execute(count_base)).scalar_one()
    query = base.order_by(Vote.vote_date.desc()).offset((page - 1) * size).limit(size)
    rows = (await session.execute(query)).all()

    results = []
    for vr, vote, bill in rows:
        results.append({
            "vote_id": vote.vote_id,
            "bill_id": bill.bill_id,
            "bill_name": bill.bill_name,
            "vote_date": vote.vote_date,
            "vote_result": vr.vote_result,
            "overall_result": vote.result,
        })
    return results, total

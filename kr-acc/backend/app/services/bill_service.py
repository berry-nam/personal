"""Bill query service."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Bill, BillSponsor, Politician


async def list_bills(
    session: AsyncSession,
    *,
    keyword: str | None = None,
    proposer_type: str | None = None,
    committee_name: str | None = None,
    result: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    assembly_term: int | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Bill], int]:
    """List bills with filtering and pagination."""
    query = select(Bill)
    count_query = select(func.count(Bill.id))

    if assembly_term is not None:
        query = query.where(Bill.assembly_term == assembly_term)
        count_query = count_query.where(Bill.assembly_term == assembly_term)

    if keyword:
        filt = Bill.bill_name.ilike(f"%{keyword}%")
        query = query.where(filt)
        count_query = count_query.where(filt)
    if proposer_type:
        query = query.where(Bill.proposer_type == proposer_type)
        count_query = count_query.where(Bill.proposer_type == proposer_type)
    if committee_name:
        filt = Bill.committee_name.ilike(f"%{committee_name}%")
        query = query.where(filt)
        count_query = count_query.where(filt)
    if result:
        query = query.where(Bill.result == result)
        count_query = count_query.where(Bill.result == result)
    if date_from:
        query = query.where(Bill.propose_date >= date_from)
        count_query = count_query.where(Bill.propose_date >= date_from)
    if date_to:
        query = query.where(Bill.propose_date <= date_to)
        count_query = count_query.where(Bill.propose_date <= date_to)

    total = (await session.execute(count_query)).scalar_one()
    query = query.order_by(Bill.propose_date.desc()).offset((page - 1) * size).limit(size)
    rows = await session.execute(query)
    return list(rows.scalars().all()), total


async def get_bill(session: AsyncSession, bill_id: str) -> Bill | None:
    """Get a single bill by bill_id with sponsors eagerly loaded."""
    result = await session.execute(
        select(Bill)
        .where(Bill.bill_id == bill_id)
        .options(selectinload(Bill.sponsors).selectinload(BillSponsor.politician))
    )
    return result.scalar_one_or_none()


async def get_pipeline_stats(
    session: AsyncSession,
    assembly_term: int | None = None,
) -> list[dict]:
    """Get bill pipeline stats — count per result/status."""
    query = select(
        Bill.result,
        func.count(Bill.id).label("count"),
    )
    if assembly_term is not None:
        query = query.where(Bill.assembly_term == assembly_term)
    query = query.group_by(Bill.result).order_by(func.count(Bill.id).desc())
    result = await session.execute(query)
    return [{"result": r or "계류중", "count": c} for r, c in result.all()]


async def get_bills_by_politician(
    session: AsyncSession,
    politician_id: int,
    *,
    sponsor_type: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Bill], int]:
    """Get bills sponsored by a politician."""
    base = (
        select(Bill)
        .join(BillSponsor, BillSponsor.bill_id == Bill.bill_id)
        .where(BillSponsor.politician_id == politician_id)
    )
    count_base = (
        select(func.count(Bill.id))
        .join(BillSponsor, BillSponsor.bill_id == Bill.bill_id)
        .where(BillSponsor.politician_id == politician_id)
    )
    if sponsor_type:
        base = base.where(BillSponsor.sponsor_type == sponsor_type)
        count_base = count_base.where(BillSponsor.sponsor_type == sponsor_type)

    total = (await session.execute(count_base)).scalar_one()
    query = base.order_by(Bill.propose_date.desc()).offset((page - 1) * size).limit(size)
    rows = await session.execute(query)
    return list(rows.scalars().all()), total

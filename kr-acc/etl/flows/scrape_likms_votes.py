"""Prefect flow: scrape per-member vote records from LIKMS.

Finds all votes in the DB that lack per-member records, scrapes LIKMS
for each bill, and upserts the individual vote records.
"""

import logging
import os

from prefect import flow, task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from scrapers.likms import LikmsScraper

logger = logging.getLogger(__name__)


def _get_session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(database_url, echo=False)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@task(name="get-votes-without-records")
async def get_votes_without_records(
    database_url: str,
    limit: int | None = None,
) -> list[tuple[str, str]]:
    """Get (vote_id, bill_id) pairs for votes that have no per-member records."""
    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        query = """
            SELECT v.vote_id, v.bill_id
            FROM votes v
            LEFT JOIN vote_records vr ON v.vote_id = vr.vote_id
            WHERE vr.id IS NULL
            ORDER BY v.vote_date DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        result = await session.execute(text(query))
        return [(row[0], row[1]) for row in result.fetchall()]


@task(name="upsert-likms-vote-records")
async def upsert_likms_vote_records(
    vote_id: str,
    member_votes: list[dict],
    database_url: str,
) -> int:
    """Upsert per-member vote records from LIKMS scrape.

    Matches member names to politician IDs in the DB.
    """
    if not member_votes:
        return 0

    session_factory = _get_session_factory(database_url)
    count = 0

    async with session_factory() as session:
        for mv in member_votes:
            # Look up politician by name
            result = await session.execute(
                text("SELECT id FROM politicians WHERE name = :name LIMIT 1"),
                {"name": mv["name"]},
            )
            row = result.fetchone()
            if not row:
                logger.debug("Politician not found: %s", mv["name"])
                continue

            politician_id = row[0]
            await session.execute(
                text("""
                    INSERT INTO vote_records (vote_id, politician_id, vote_result)
                    VALUES (:vote_id, :politician_id, :vote_result)
                    ON CONFLICT (vote_id, politician_id) DO UPDATE SET
                        vote_result = EXCLUDED.vote_result
                """),
                {
                    "vote_id": vote_id,
                    "politician_id": politician_id,
                    "vote_result": mv["vote_result"],
                },
            )
            count += 1

        await session.commit()
    return count


@flow(name="scrape-likms-votes", log_prints=True)
async def scrape_likms_votes(
    database_url: str | None = None,
    limit: int | None = None,
    bill_ids: list[str] | None = None,
) -> dict:
    """Scrape per-member vote data from LIKMS for votes missing records.

    Args:
        database_url: Database URL.
        limit: Max number of votes to process.
        bill_ids: Specific bill IDs to scrape (overrides DB lookup).

    Returns:
        Dict with scrape stats.
    """
    database_url = database_url or os.environ["DATABASE_URL"]

    if bill_ids:
        # Manual bill IDs — look up vote IDs
        session_factory = _get_session_factory(database_url)
        vote_pairs = []
        async with session_factory() as session:
            for bid in bill_ids:
                result = await session.execute(
                    text("SELECT vote_id FROM votes WHERE bill_id = :bid LIMIT 1"),
                    {"bid": bid},
                )
                row = result.fetchone()
                if row:
                    vote_pairs.append((row[0], bid))
                else:
                    print(f"  No vote found for bill: {bid}")
    else:
        vote_pairs = await get_votes_without_records(database_url, limit=limit)

    if not vote_pairs:
        print("No votes need per-member records.")
        return {"scraped": 0, "records_upserted": 0}

    print(f"Scraping LIKMS for {len(vote_pairs)} votes...")

    scraper = LikmsScraper(rate_limit=1.5)  # Conservative rate limit
    bill_ids_to_scrape = [bid for _, bid in vote_pairs]
    vote_id_by_bill = {bid: vid for vid, bid in vote_pairs}

    details = await scraper.fetch_bills_batch(bill_ids_to_scrape, concurrency=2)

    total_records = 0
    scraped = 0
    for bill_id, detail in details.items():
        if detail is None:
            continue
        scraped += 1
        vote_id = vote_id_by_bill[bill_id]
        member_dicts = [
            {"name": mv.name, "vote_result": mv.vote_result}
            for mv in detail.member_votes
        ]
        count = await upsert_likms_vote_records(vote_id, member_dicts, database_url)
        total_records += count
        if count > 0:
            print(
                f"  {bill_id}: {count} records "
                f"(Y:{detail.yes_count} N:{detail.no_count} A:{detail.abstain_count})"
            )

    print(f"\nLIKMS scrape complete:")
    print(f"  Votes processed: {scraped}/{len(vote_pairs)}")
    print(f"  Records upserted: {total_records}")

    return {
        "scraped": scraped,
        "records_upserted": total_records,
    }


if __name__ == "__main__":
    import asyncio
    import sys

    bill_args = sys.argv[1:] if len(sys.argv) > 1 else None
    asyncio.run(scrape_likms_votes(bill_ids=bill_args, limit=10 if not bill_args else None))

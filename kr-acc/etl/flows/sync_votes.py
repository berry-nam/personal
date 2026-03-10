"""Prefect flow: sync voting records from 열린국회정보 API.

Requires bills to be synced first (FK dependency). Makes two API calls
per vote: one for the summary, then per-member details.
"""

import logging
import os

from prefect import flow

from tasks.extract import extract_vote_members, extract_vote_summaries
from tasks.load import load_vote_records, load_vote_summaries
from tasks.transform import transform_vote_members, transform_vote_summaries
from tasks.validate import validate_vote_summaries

logger = logging.getLogger(__name__)


@flow(name="sync-votes", log_prints=True)
async def sync_votes(
    api_key: str | None = None,
    database_url: str | None = None,
    assembly_term: int = 22,
) -> dict:
    """Sync plenary vote data and per-member vote records.

    Args:
        api_key: Assembly API key.
        database_url: Database URL.
        assembly_term: Assembly term number.

    Returns:
        Dict with counts of synced records.
    """
    api_key = api_key or os.environ["ASSEMBLY_API_KEY"]
    database_url = database_url or os.environ["DATABASE_URL"]

    # Extract vote summaries
    raw_summaries = await extract_vote_summaries(api_key, assembly_term)

    # Transform and validate
    summaries = transform_vote_summaries(raw_summaries, assembly_term)
    summaries = validate_vote_summaries(summaries)

    # Load vote summaries
    summary_count = await load_vote_summaries(summaries, database_url)

    # For each vote, fetch and load per-member records
    member_record_count = 0
    for summary in summaries:
        bill_id = summary["bill_id"]
        vote_id = summary["vote_id"]

        raw_members = await extract_vote_members(api_key, bill_id)
        if not raw_members:
            continue

        member_records = transform_vote_members(raw_members, vote_id)
        count = await load_vote_records(member_records, database_url)
        member_record_count += count

    print(
        f"Synced {summary_count} vote summaries, "
        f"{member_record_count} individual vote records"
    )
    return {
        "vote_summaries": summary_count,
        "vote_records": member_record_count,
    }


if __name__ == "__main__":
    import asyncio

    asyncio.run(sync_votes())

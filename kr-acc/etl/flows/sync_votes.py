"""Prefect flow: sync voting records from 열린국회정보 API.

Requires bills to be synced first (FK dependency on bill_id).
Loads vote summaries (per-bill aggregate counts).
Per-member vote records are not currently available from the Open API.
"""

import logging
import os

from prefect import flow

from tasks.extract import extract_vote_summaries
from tasks.load import load_vote_summaries
from tasks.transform import transform_vote_summaries
from tasks.validate import validate_vote_summaries

logger = logging.getLogger(__name__)


@flow(name="sync-votes", log_prints=True)
async def sync_votes(
    api_key: str | None = None,
    database_url: str | None = None,
    assembly_term: int = 22,
) -> dict:
    """Sync plenary vote data (bill-level summaries).

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

    print(f"Synced {summary_count} vote summaries for term {assembly_term}")
    return {
        "vote_summaries": summary_count,
        "vote_records": 0,
    }


if __name__ == "__main__":
    import asyncio

    asyncio.run(sync_votes())

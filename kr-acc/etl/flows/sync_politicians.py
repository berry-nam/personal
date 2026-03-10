"""Prefect flow: sync legislator data from 열린국회정보 API.

Simplest flow — ~300 records for the 22nd Assembly.
"""

import logging
import os

from prefect import flow

from tasks.extract import extract_committees, extract_legislators
from tasks.load import load_committees, load_politicians, sync_age_politicians
from tasks.transform import transform_committees, transform_legislators
from tasks.validate import validate_legislators

logger = logging.getLogger(__name__)


@flow(name="sync-politicians", log_prints=True)
async def sync_politicians(
    api_key: str | None = None,
    database_url: str | None = None,
    assembly_term: int = 22,
) -> dict:
    """Sync legislator and committee data.

    Args:
        api_key: Assembly API key (defaults to ASSEMBLY_API_KEY env var).
        database_url: Database URL (defaults to DATABASE_URL env var).
        assembly_term: Assembly term number.

    Returns:
        Dict with counts of synced records.
    """
    api_key = api_key or os.environ["ASSEMBLY_API_KEY"]
    database_url = database_url or os.environ["DATABASE_URL"]

    # Extract
    raw_legislators = await extract_legislators(api_key, assembly_term)
    raw_committees = await extract_committees(api_key)

    # Transform
    legislators = transform_legislators(raw_legislators, assembly_term)
    committees = transform_committees(raw_committees, assembly_term)

    # Validate
    legislators = validate_legislators(legislators)

    # Load
    pol_count = await load_politicians(legislators, database_url)
    com_count = await load_committees(committees, database_url)

    # Sync to AGE graph
    graph_count = await sync_age_politicians(database_url)

    print(f"Synced {pol_count} politicians, {com_count} committees, {graph_count} graph nodes")
    return {
        "politicians": pol_count,
        "committees": com_count,
        "graph_nodes": graph_count,
    }


if __name__ == "__main__":
    import asyncio

    asyncio.run(sync_politicians())

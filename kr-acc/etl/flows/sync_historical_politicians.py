"""Prefect flow: sync historical legislators from ALLNAMEMBER endpoint.

Fetches all-time legislator data and upserts politicians from terms 17-21
(or any specified historical terms). Term 22 is handled by the regular
sync_politicians flow using the LEGISLATORS endpoint.
"""

import logging
import os

from prefect import flow

from tasks.extract import extract_all_legislators
from tasks.load import load_politicians, sync_age_politicians
from tasks.transform import transform_all_legislators

logger = logging.getLogger(__name__)

HISTORICAL_TERMS = [17, 18, 19, 20, 21]


@flow(name="sync-historical-politicians", log_prints=True)
async def sync_historical_politicians(
    api_key: str | None = None,
    database_url: str | None = None,
    target_terms: list[int] | None = None,
) -> dict:
    """Sync historical legislator data from ALLNAMEMBER API.

    Args:
        api_key: Assembly API key.
        database_url: Database URL.
        target_terms: Which terms to include (default: 17-21).

    Returns:
        Dict with counts of synced records.
    """
    api_key = api_key or os.environ["ASSEMBLY_API_KEY"]
    database_url = database_url or os.environ["DATABASE_URL"]
    terms = target_terms or HISTORICAL_TERMS

    # Extract all-time legislators
    raw_rows = await extract_all_legislators(api_key)

    # Transform — filter to target terms only
    legislators = transform_all_legislators(raw_rows, target_terms=terms)

    # Load
    pol_count = await load_politicians(legislators, database_url)

    # Sync to AGE graph
    graph_count = await sync_age_politicians(database_url)

    print(f"Synced {pol_count} historical politicians (terms {terms}), {graph_count} graph nodes")
    return {
        "historical_politicians": pol_count,
        "graph_nodes": graph_count,
    }


if __name__ == "__main__":
    import asyncio

    asyncio.run(sync_historical_politicians())

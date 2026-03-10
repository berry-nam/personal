"""Prefect flow: orchestrate all ETL pipelines in order.

Execution order matters due to FK dependencies:
1. Politicians + Committees (no dependencies)
2. Bills + Sponsors (needs politicians for name matching)
3. Votes (needs bills for FK)
4. Co-sponsorship graph (needs bill_sponsors)
"""

import logging
import os

from prefect import flow

from flows.compute_co_sponsorship import compute_co_sponsorship
from flows.sync_bills import sync_bills
from flows.sync_politicians import sync_politicians
from flows.sync_votes import sync_votes

logger = logging.getLogger(__name__)


@flow(name="sync-all", log_prints=True)
async def sync_all(
    api_key: str | None = None,
    database_url: str | None = None,
    assembly_term: int = 22,
) -> dict:
    """Run all ETL pipelines in dependency order.

    Args:
        api_key: Assembly API key.
        database_url: Database URL.
        assembly_term: Assembly term number.

    Returns:
        Combined results from all sub-flows.
    """
    api_key = api_key or os.environ["ASSEMBLY_API_KEY"]
    database_url = database_url or os.environ["DATABASE_URL"]

    print("=" * 60)
    print("Starting full ETL sync")
    print("=" * 60)

    # Step 1: Politicians and committees
    print("\n[1/4] Syncing politicians and committees...")
    pol_result = await sync_politicians(api_key, database_url, assembly_term)

    # Step 2: Bills and sponsors
    print("\n[2/4] Syncing bills and sponsors...")
    bill_result = await sync_bills(api_key, database_url, assembly_term)

    # Step 3: Votes
    print("\n[3/4] Syncing votes...")
    vote_result = await sync_votes(api_key, database_url, assembly_term)

    # Step 4: Co-sponsorship graph
    print("\n[4/4] Computing co-sponsorship network...")
    graph_result = await compute_co_sponsorship(database_url)

    print("\n" + "=" * 60)
    print("ETL sync complete!")
    print(f"  Politicians: {pol_result['politicians']}")
    print(f"  Committees:  {pol_result['committees']}")
    print(f"  Bills:       {bill_result['bills']}")
    print(f"  Sponsors:    {bill_result['sponsor_links']}")
    print(f"  Votes:       {vote_result['vote_summaries']}")
    print(f"  Vote records:{vote_result['vote_records']}")
    print(f"  Graph edges: {graph_result['co_sponsorship_edges']}")
    print("=" * 60)

    return {
        **pol_result,
        **bill_result,
        **vote_result,
        **graph_result,
    }


if __name__ == "__main__":
    import asyncio

    asyncio.run(sync_all())

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


DEFAULT_TERMS = [17, 18, 19, 20, 21, 22]


@flow(name="sync-all", log_prints=True)
async def sync_all(
    api_key: str | None = None,
    database_url: str | None = None,
    assembly_terms: list[int] | None = None,
) -> dict:
    """Run all ETL pipelines in dependency order for multiple assembly terms.

    Args:
        api_key: Assembly API key.
        database_url: Database URL.
        assembly_terms: List of assembly term numbers (default: 17~22).

    Returns:
        Combined results from all sub-flows.
    """
    api_key = api_key or os.environ["ASSEMBLY_API_KEY"]
    database_url = database_url or os.environ["DATABASE_URL"]
    terms = assembly_terms or DEFAULT_TERMS

    print("=" * 60)
    print(f"Starting full ETL sync for terms: {terms}")
    print("=" * 60)

    totals = {
        "politicians": 0, "committees": 0, "graph_nodes": 0,
        "bills": 0, "sponsor_links": 0,
        "vote_summaries": 0, "vote_records": 0,
    }

    for term in terms:
        print(f"\n{'─' * 40}")
        print(f"  Term {term}대")
        print(f"{'─' * 40}")

        # Step 1: Politicians and committees
        print(f"\n[1/3] Syncing politicians and committees (term {term})...")
        pol_result = await sync_politicians(api_key, database_url, term)
        for k in ("politicians", "committees", "graph_nodes"):
            totals[k] += pol_result.get(k, 0)

        # Step 2: Bills and sponsors
        print(f"\n[2/3] Syncing bills and sponsors (term {term})...")
        bill_result = await sync_bills(api_key, database_url, term)
        for k in ("bills", "sponsor_links"):
            totals[k] += bill_result.get(k, 0)

        # Step 3: Votes
        print(f"\n[3/3] Syncing votes (term {term})...")
        vote_result = await sync_votes(api_key, database_url, term)
        for k in ("vote_summaries", "vote_records"):
            totals[k] += vote_result.get(k, 0)

    # Final step: Co-sponsorship graph (across all terms)
    print("\nComputing co-sponsorship network (all terms)...")
    graph_result = await compute_co_sponsorship(database_url)

    print("\n" + "=" * 60)
    print("ETL sync complete!")
    print(f"  Terms:       {terms}")
    print(f"  Politicians: {totals['politicians']}")
    print(f"  Committees:  {totals['committees']}")
    print(f"  Bills:       {totals['bills']}")
    print(f"  Sponsors:    {totals['sponsor_links']}")
    print(f"  Votes:       {totals['vote_summaries']}")
    print(f"  Vote records:{totals['vote_records']}")
    print(f"  Graph edges: {graph_result['co_sponsorship_edges']}")
    print("=" * 60)

    return {**totals, **graph_result}


if __name__ == "__main__":
    import asyncio

    asyncio.run(sync_all())

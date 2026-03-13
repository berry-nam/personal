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
from flows.scrape_likms_votes import scrape_likms_votes
from flows.scrape_newstapa import scrape_newstapa
from flows.sync_bills import sync_bills
from flows.sync_companies import sync_companies
from flows.sync_historical_politicians import sync_historical_politicians
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
        "historical_politicians": 0,
    }

    # Step 0: Sync historical politicians (terms 17-21) from ALLNAMEMBER
    historical_terms = [t for t in terms if t < 22]
    if historical_terms:
        print("\n[0] Syncing historical politicians from ALLNAMEMBER...")
        hist_result = await sync_historical_politicians(
            api_key, database_url, target_terms=historical_terms
        )
        totals["historical_politicians"] = hist_result.get("historical_politicians", 0)

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

    # Optional: Sync company data from DART
    dart_key = os.environ.get("DART_API_KEY", "")
    companies_synced = 0
    if dart_key:
        print("\nSyncing company data from DART...")
        company_result = await sync_companies(dart_key, database_url)
        companies_synced = company_result.get("companies_synced", 0)
    else:
        print("\nSkipping DART company sync (DART_API_KEY not set)")

    # Scrape per-member vote records from LIKMS
    print("\nScraping per-member votes from LIKMS...")
    likms_result = await scrape_likms_votes(database_url)
    likms_records = likms_result.get("records_upserted", 0)

    # Scrape asset declarations from Newstapa
    print("\nScraping asset declarations from Newstapa...")
    newstapa_result = await scrape_newstapa(database_url)
    newstapa_declarations = newstapa_result.get("declarations_upserted", 0)

    print("\n" + "=" * 60)
    print("ETL sync complete!")
    print(f"  Terms:       {terms}")
    print(f"  Historical:  {totals['historical_politicians']}")
    print(f"  Politicians: {totals['politicians']}")
    print(f"  Committees:  {totals['committees']}")
    print(f"  Bills:       {totals['bills']}")
    print(f"  Sponsors:    {totals['sponsor_links']}")
    print(f"  Votes:       {totals['vote_summaries']}")
    print(f"  Vote records:{totals['vote_records']}")
    print(f"  Graph edges: {graph_result['co_sponsorship_edges']}")
    print(f"  Companies:   {companies_synced}")
    print(f"  LIKMS votes: {likms_records}")
    print(f"  Newstapa:    {newstapa_declarations}")
    print("=" * 60)

    return {
        **totals,
        **graph_result,
        "companies_synced": companies_synced,
        "likms_vote_records": likms_records,
        "newstapa_declarations": newstapa_declarations,
    }


if __name__ == "__main__":
    import asyncio

    asyncio.run(sync_all())

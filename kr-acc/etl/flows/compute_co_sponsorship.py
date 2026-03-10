"""Prefect flow: compute co-sponsorship network and sync to Apache AGE.

Aggregates bill_sponsors data to find pairs of politicians who co-sponsor
bills together, then creates weighted CO_SPONSORED edges in the graph.
"""

import logging
import os

from prefect import flow

from tasks.load import sync_age_co_sponsorship

logger = logging.getLogger(__name__)


@flow(name="compute-co-sponsorship", log_prints=True)
async def compute_co_sponsorship(
    database_url: str | None = None,
    graph_name: str = "kr_acc",
) -> dict:
    """Compute co-sponsorship edges and sync to AGE graph.

    Args:
        database_url: Database URL.
        graph_name: AGE graph name.

    Returns:
        Dict with count of edges created.
    """
    database_url = database_url or os.environ["DATABASE_URL"]

    edge_count = await sync_age_co_sponsorship(database_url, graph_name)

    print(f"Computed {edge_count} co-sponsorship edges (weight >= 3 shared bills)")
    return {"co_sponsorship_edges": edge_count}


if __name__ == "__main__":
    import asyncio

    asyncio.run(compute_co_sponsorship())

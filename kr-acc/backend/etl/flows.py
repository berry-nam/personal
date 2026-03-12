"""Prefect flows for kr-acc ETL pipeline.

Flows:
  - sync_politicians: Daily sync of 300 legislators
  - sync_bills: Daily sync of all bills for current term
  - sync_votes: Daily sync of plenary vote records
  - compute_co_sponsorship: Weekly co-sponsorship edge computation
  - full_sync: Orchestrates all flows in order
"""

import logging

from prefect import flow, task
from prefect.logging import get_run_logger

from etl import api_client, db, transforms
from etl.config import ASSEMBLY_TERM

# ── Tasks ────────────────────────────────────────────────────────────────────


@task(retries=2, retry_delay_seconds=10)
async def fetch_politicians_data() -> list[dict]:
    """Fetch raw politician data from 열린국회정보 API."""
    return await api_client.fetch_all_pages(
        "politicians",
        params={"AGE": str(ASSEMBLY_TERM)},
    )


@task
def transform_and_load_politicians(raw_rows: list[dict]) -> int:
    """Transform and upsert politician data."""
    transformed = transforms.transform_politicians(raw_rows)
    parties = transforms.extract_unique_parties(transformed)
    db.upsert_parties(parties)
    return db.upsert_politicians(transformed)


@task(retries=2, retry_delay_seconds=10)
async def fetch_bills_data() -> list[dict]:
    """Fetch raw bill data from 열린국회정보 API."""
    return await api_client.fetch_all_pages(
        "bills",
        params={"AGE": str(ASSEMBLY_TERM)},
    )


@task
def transform_and_load_bills(raw_rows: list[dict]) -> int:
    """Transform and upsert bill data."""
    transformed = transforms.transform_bills(raw_rows)
    return db.upsert_bills(transformed)


@task(retries=2, retry_delay_seconds=10)
async def fetch_votes_data() -> list[dict]:
    """Fetch raw plenary vote data."""
    return await api_client.fetch_all_pages(
        "vote_results",
        params={"AGE": str(ASSEMBLY_TERM)},
    )


@task
def transform_and_load_votes(raw_rows: list[dict]) -> int:
    """Transform and upsert vote summary data."""
    transformed = transforms.transform_votes(raw_rows)
    return db.upsert_votes(transformed)


@task(retries=2, retry_delay_seconds=30)
async def fetch_and_load_vote_records(vote_id: str, politician_id_map: dict[str, int]) -> int:
    """Fetch per-member vote records for a single vote and load them."""
    raw = await api_client.fetch_single(
        "vote_records",
        params={"BILL_ID": vote_id, "AGE": str(ASSEMBLY_TERM)},
    )
    records = transforms.transform_vote_records(raw, vote_id, politician_id_map)
    return db.upsert_vote_records(records)


@task
def sync_graph_politicians() -> None:
    """Sync Politician nodes to AGE graph."""
    db.sync_age_politicians()


@task
def compute_graph_edges() -> int:
    """Compute CO_SPONSORED edges."""
    return db.compute_co_sponsorship_edges()


@task
def get_politician_lookup() -> dict[str, int]:
    """Get assembly_id → id mapping for politician name resolution."""
    return db.get_politician_id_map()


# ── Flows ────────────────────────────────────────────────────────────────────


@flow(name="sync-politicians", log_prints=True)
async def sync_politicians() -> int:
    """Daily flow: sync legislator data from 열린국회정보 API."""
    logger = get_run_logger()
    raw = await fetch_politicians_data()
    count = transform_and_load_politicians(raw)
    sync_graph_politicians()
    logger.info("Synced %d politicians", count)
    return count


@flow(name="sync-bills", log_prints=True)
async def sync_bills() -> int:
    """Daily flow: sync bill/legislation data."""
    logger = get_run_logger()
    raw = await fetch_bills_data()
    count = transform_and_load_bills(raw)
    logger.info("Synced %d bills", count)
    return count


@flow(name="sync-votes", log_prints=True)
async def sync_votes() -> int:
    """Daily flow: sync plenary vote data + per-member records."""
    logger = get_run_logger()
    raw = await fetch_votes_data()
    count = transform_and_load_votes(raw)
    logger.info("Synced %d vote summaries", count)

    # Fetch per-member records for each vote
    pid_map = get_politician_lookup()
    record_count = 0
    for vote_row in raw:
        vote_id = vote_row.get("BILL_ID", "").strip()
        if vote_id:
            rc = await fetch_and_load_vote_records(vote_id, pid_map)
            record_count += rc

    logger.info("Synced %d individual vote records", record_count)
    return count


@flow(name="compute-co-sponsorship", log_prints=True)
def compute_co_sponsorship() -> int:
    """Weekly flow: compute co-sponsorship edges in the graph."""
    logger = get_run_logger()
    edge_count = compute_graph_edges()
    logger.info("Computed %d co-sponsorship edges", edge_count)
    return edge_count


@flow(name="full-sync", log_prints=True)
async def full_sync() -> dict[str, int]:
    """Orchestration flow: runs all ETL steps in order.

    1. Sync politicians (must be first — other flows reference politician IDs)
    2. Sync bills
    3. Sync votes + per-member records
    4. Compute co-sponsorship edges
    """
    logger = get_run_logger()
    logger.info("Starting full ETL sync for term %d", ASSEMBLY_TERM)

    pol_count = await sync_politicians()
    bill_count = await sync_bills()
    vote_count = await sync_votes()
    edge_count = compute_co_sponsorship()

    result = {
        "politicians": pol_count,
        "bills": bill_count,
        "votes": vote_count,
        "co_sponsorship_edges": edge_count,
    }
    logger.info("Full sync complete: %s", result)
    return result

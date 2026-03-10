"""Extract tasks — fetch data from 열린국회정보 API."""

import logging

from prefect import task

from assembly_client import (
    BILLS,
    COMMITTEES,
    LEGISLATORS,
    VOTE_PER_MEMBER,
    VOTE_SUMMARY,
    AssemblyClient,
)

logger = logging.getLogger(__name__)


@task(name="extract-legislators", retries=2, retry_delay_seconds=10)
async def extract_legislators(api_key: str, assembly_term: int = 22) -> list[dict]:
    """Fetch all legislator records for the given assembly term."""
    async with AssemblyClient(api_key=api_key) as client:
        rows = await client.fetch_all(LEGISLATORS, params={"AGE": str(assembly_term)})
    logger.info("Extracted %d legislators for term %d", len(rows), assembly_term)
    return rows


@task(name="extract-bills", retries=2, retry_delay_seconds=10)
async def extract_bills(api_key: str, assembly_term: int = 22) -> list[dict]:
    """Fetch all bill records for the given assembly term."""
    async with AssemblyClient(api_key=api_key) as client:
        rows = await client.fetch_all(
            BILLS, params={"AGE": str(assembly_term)}, size=100
        )
    logger.info("Extracted %d bills for term %d", len(rows), assembly_term)
    return rows


@task(name="extract-vote-summaries", retries=2, retry_delay_seconds=10)
async def extract_vote_summaries(api_key: str, assembly_term: int = 22) -> list[dict]:
    """Fetch all plenary vote summaries for the given assembly term."""
    async with AssemblyClient(api_key=api_key) as client:
        rows = await client.fetch_all(
            VOTE_SUMMARY, params={"AGE": str(assembly_term)}, size=100
        )
    logger.info("Extracted %d vote summaries for term %d", len(rows), assembly_term)
    return rows


@task(name="extract-vote-members", retries=2, retry_delay_seconds=30)
async def extract_vote_members(api_key: str, bill_id: str) -> list[dict]:
    """Fetch per-member vote records for a specific bill."""
    async with AssemblyClient(api_key=api_key) as client:
        rows = await client.fetch_all(VOTE_PER_MEMBER, params={"BILL_ID": bill_id})
    return rows


@task(name="extract-committees", retries=2, retry_delay_seconds=10)
async def extract_committees(api_key: str) -> list[dict]:
    """Fetch all committee records."""
    async with AssemblyClient(api_key=api_key) as client:
        rows = await client.fetch_all(COMMITTEES)
    logger.info("Extracted %d committee records", len(rows))
    return rows

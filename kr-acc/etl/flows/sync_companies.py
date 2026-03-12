"""Prefect flow: sync company data from DART Open API.

Requires DART_API_KEY environment variable.
Downloads corporate disclosure data for companies linked to politicians.
"""

import logging
import os

from prefect import flow, task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dart_client.client import DartClient, DartAPIError

logger = logging.getLogger(__name__)


def _get_session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(database_url, echo=False)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@task(name="fetch-company-from-dart")
async def fetch_company(client: DartClient, corp_code: str) -> dict | None:
    """Fetch a single company's info from DART."""
    try:
        data = await client.get_company(corp_code)
        if data.get("status") == "013":
            return None
        return data
    except DartAPIError as e:
        logger.warning("DART API error for %s: %s", corp_code, e)
        return None


@task(name="upsert-company")
async def upsert_company(company_data: dict, database_url: str) -> bool:
    """Upsert a company record from DART data."""
    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        await session.execute(
            text("""
                INSERT INTO companies (corp_code, corp_name, stock_code, industry, ceo_name, homepage)
                VALUES (:corp_code, :corp_name, :stock_code, :industry, :ceo_name, :homepage)
                ON CONFLICT (corp_code) DO UPDATE SET
                    corp_name = EXCLUDED.corp_name,
                    stock_code = EXCLUDED.stock_code,
                    industry = EXCLUDED.industry,
                    ceo_name = EXCLUDED.ceo_name,
                    homepage = EXCLUDED.homepage
            """),
            {
                "corp_code": company_data.get("corp_code", ""),
                "corp_name": company_data.get("corp_name", ""),
                "stock_code": company_data.get("stock_code") or None,
                "industry": company_data.get("induty_code") or None,
                "ceo_name": company_data.get("ceo_nm") or None,
                "homepage": company_data.get("hm_url") or None,
            },
        )
        await session.commit()
    return True


@task(name="get-linked-corp-codes")
async def get_linked_corp_codes(database_url: str) -> list[str]:
    """Get all corp_codes from companies that are linked to politicians."""
    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        result = await session.execute(
            text("""
                SELECT DISTINCT c.corp_code
                FROM companies c
                JOIN politician_companies pc ON pc.company_id = c.id
                WHERE c.corp_code IS NOT NULL AND c.corp_code != ''
            """)
        )
        return [row[0] for row in result.fetchall()]


@flow(name="sync-companies", log_prints=True)
async def sync_companies(
    dart_api_key: str | None = None,
    database_url: str | None = None,
) -> dict:
    """Sync company data from DART Open API.

    Fetches updated corporate info for all companies linked to politicians.

    Args:
        dart_api_key: DART API key.
        database_url: Database URL.

    Returns:
        Dict with counts.
    """
    dart_api_key = dart_api_key or os.environ.get("DART_API_KEY", "")
    database_url = database_url or os.environ["DATABASE_URL"]

    if not dart_api_key:
        print("WARNING: DART_API_KEY not set. Skipping company sync.")
        return {"companies_synced": 0, "skipped": True}

    corp_codes = await get_linked_corp_codes(database_url)
    print(f"Found {len(corp_codes)} companies to sync from DART")

    synced = 0
    async with DartClient(dart_api_key) as client:
        for corp_code in corp_codes:
            data = await fetch_company(client, corp_code)
            if data:
                await upsert_company(data, database_url)
                synced += 1
                print(f"  Synced: {data.get('corp_name', corp_code)}")

    print(f"Synced {synced}/{len(corp_codes)} companies from DART")
    return {"companies_synced": synced}


if __name__ == "__main__":
    import asyncio

    asyncio.run(sync_companies())

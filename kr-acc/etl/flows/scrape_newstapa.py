"""Prefect flow: scrape asset declarations from Newstapa (jaesan.newstapa.org).

Looks up all politicians in the DB, searches each on Newstapa, and upserts
asset declarations and individual items.
"""

import json
import logging
import os

from prefect import flow, task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from scrapers.newstapa import NewstapaProfile, NewstapaScraper

logger = logging.getLogger(__name__)


def _get_session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(database_url, echo=False)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Map Newstapa category names to our DB category values
CATEGORY_MAP = {
    "토지": "real_estate",
    "건물": "real_estate",
    "예금": "deposit",
    "증권": "securities",
    "채권": "securities",
    "자동차·선박 등": "vehicle",
    "자동차": "vehicle",
    "채무": "other",
    "기타": "other",
    "가상자산": "crypto",
}


def _map_category(raw_category: str) -> str:
    """Map Korean category name to DB category slug."""
    for key, value in CATEGORY_MAP.items():
        if key in raw_category:
            return value
    return "other"


@task(name="get-politician-names")
async def get_politician_names(database_url: str) -> list[tuple[int, str]]:
    """Get all politician (id, name) pairs from the DB."""
    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        result = await session.execute(
            text("SELECT id, name FROM politicians ORDER BY id")
        )
        return [(row[0], row[1]) for row in result.fetchall()]


@task(name="upsert-newstapa-assets")
async def upsert_newstapa_assets(
    politician_id: int,
    profile: NewstapaProfile,
    database_url: str,
) -> int:
    """Upsert asset declarations and items from a Newstapa profile."""
    session_factory = _get_session_factory(database_url)
    count = 0

    async with session_factory() as session:
        for yearly in profile.yearly_assets:
            if yearly.total_assets is None:
                continue

            # Compute category totals from breakdown
            real_estate = 0
            deposits = 0
            securities = 0
            crypto = 0
            for item in yearly.breakdown:
                if item.amount_krw is None:
                    continue
                cat = _map_category(item.category)
                if cat == "real_estate":
                    real_estate += item.amount_krw
                elif cat == "deposit":
                    deposits += item.amount_krw
                elif cat == "securities":
                    securities += item.amount_krw
                elif cat == "crypto":
                    crypto += item.amount_krw

            # Build raw_data JSON
            raw_data = {
                "url": f"https://jaesan.newstapa.org{profile.url_path}",
                "breakdown": [
                    {
                        "category": b.category,
                        "percentage": b.percentage,
                        "amount_text": b.amount_text,
                        "amount_krw": b.amount_krw,
                    }
                    for b in yearly.breakdown
                ],
            }

            # Upsert declaration
            result = await session.execute(
                text("""
                    INSERT INTO asset_declarations
                        (politician_id, report_year, total_assets, total_real_estate,
                         total_deposits, total_securities, total_crypto, source, raw_data)
                    VALUES
                        (:politician_id, :report_year, :total_assets, :total_real_estate,
                         :total_deposits, :total_securities, :total_crypto, 'newstapa',
                         CAST(:raw_data AS jsonb))
                    ON CONFLICT (politician_id, report_year) DO UPDATE SET
                        total_assets = EXCLUDED.total_assets,
                        total_real_estate = EXCLUDED.total_real_estate,
                        total_deposits = EXCLUDED.total_deposits,
                        total_securities = EXCLUDED.total_securities,
                        total_crypto = EXCLUDED.total_crypto,
                        source = EXCLUDED.source,
                        raw_data = EXCLUDED.raw_data
                    RETURNING id
                """),
                {
                    "politician_id": politician_id,
                    "report_year": yearly.year,
                    "total_assets": yearly.total_assets,
                    "total_real_estate": real_estate or None,
                    "total_deposits": deposits or None,
                    "total_securities": securities or None,
                    "total_crypto": crypto or None,
                    "raw_data": json.dumps(raw_data, ensure_ascii=False),
                },
            )
            decl_row = result.fetchone()
            if not decl_row:
                continue
            declaration_id = decl_row[0]

            # Delete existing items and re-insert
            await session.execute(
                text("DELETE FROM asset_items WHERE declaration_id = :did"),
                {"did": declaration_id},
            )

            for item in yearly.breakdown:
                if item.amount_krw is None:
                    continue
                await session.execute(
                    text("""
                        INSERT INTO asset_items
                            (declaration_id, category, subcategory, value_krw, note)
                        VALUES
                            (:declaration_id, :category, :subcategory, :value_krw, :note)
                    """),
                    {
                        "declaration_id": declaration_id,
                        "category": _map_category(item.category),
                        "subcategory": item.category,
                        "value_krw": item.amount_krw,
                        "note": f"{item.percentage} ({item.amount_text})",
                    },
                )

            count += 1

        await session.commit()
    return count


@flow(name="scrape-newstapa", log_prints=True)
async def scrape_newstapa(
    database_url: str | None = None,
    limit: int | None = None,
    names: list[str] | None = None,
) -> dict:
    """Scrape asset declarations from Newstapa for politicians in the DB.

    Args:
        database_url: Database URL.
        limit: Max number of politicians to process (for testing).
        names: Specific politician names to scrape (overrides DB lookup).

    Returns:
        Dict with scrape stats.
    """
    database_url = database_url or os.environ["DATABASE_URL"]

    if names:
        # Use provided names — look up IDs
        politicians = []
        session_factory = _get_session_factory(database_url)
        async with session_factory() as session:
            for name in names:
                result = await session.execute(
                    text("SELECT id FROM politicians WHERE name = :name LIMIT 1"),
                    {"name": name},
                )
                row = result.fetchone()
                if row:
                    politicians.append((row[0], name))
                else:
                    print(f"  Politician not found in DB: {name}")
    else:
        politicians = await get_politician_names(database_url)

    if limit:
        politicians = politicians[:limit]

    print(f"Scraping Newstapa for {len(politicians)} politicians...")

    scraper = NewstapaScraper(rate_limit=2.0)
    name_list = [name for _, name in politicians]
    id_by_name = {name: pid for pid, name in politicians}

    profiles = await scraper.fetch_profiles_batch(name_list, concurrency=2)

    total_declarations = 0
    found = 0
    for name, profile in profiles.items():
        if profile is None:
            continue
        found += 1
        pid = id_by_name[name]
        count = await upsert_newstapa_assets(pid, profile, database_url)
        total_declarations += count
        if count > 0:
            print(f"  {name}: {count} year(s) of asset data")

    print(f"\nNewstapa scrape complete:")
    print(f"  Searched: {len(politicians)}")
    print(f"  Found:    {found}")
    print(f"  Declarations upserted: {total_declarations}")

    return {
        "searched": len(politicians),
        "found": found,
        "declarations_upserted": total_declarations,
    }


if __name__ == "__main__":
    import asyncio
    import sys

    # Allow testing with specific names: python scrape_newstapa.py 이재명 한동훈
    names_arg = sys.argv[1:] if len(sys.argv) > 1 else None
    asyncio.run(scrape_newstapa(names=names_arg, limit=5 if not names_arg else None))

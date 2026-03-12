"""Prefect flow: import asset declarations and political fund data from CSV files.

Supports manual data import from:
- 뉴스타파 재산공개 (jaesan.newstapa.org) exports
- 정치자금 수입·지출 보고서 (National Election Commission data)
- Manual CSV files in a standard format

CSV formats expected:

assets.csv:
  politician_name, report_year, total_assets, total_real_estate, total_deposits,
  total_securities, total_crypto, source

fund.csv:
  politician_name, fund_year, fund_type, income_total, expense_total, balance, source
"""

import csv
import logging
import os
from pathlib import Path

from prefect import flow, task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)


def _get_session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(database_url, echo=False)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _safe_int(val: str) -> int | None:
    if not val or not val.strip():
        return None
    try:
        return int(val.strip().replace(",", ""))
    except ValueError:
        return None


@task(name="resolve-politician-id")
async def resolve_politician_id(name: str, database_url: str) -> int | None:
    """Look up politician ID by name."""
    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        result = await session.execute(
            text("SELECT id FROM politicians WHERE name = :name LIMIT 1"),
            {"name": name.strip()},
        )
        row = result.fetchone()
        return row[0] if row else None


@task(name="import-asset-rows")
async def import_asset_rows(rows: list[dict], database_url: str) -> int:
    """Upsert asset declaration rows."""
    session_factory = _get_session_factory(database_url)
    count = 0
    async with session_factory() as session:
        for r in rows:
            pol_id = r.get("politician_id")
            if not pol_id:
                continue
            await session.execute(
                text("""
                    INSERT INTO asset_declarations
                        (politician_id, report_year, total_assets, total_real_estate,
                         total_deposits, total_securities, total_crypto, source)
                    VALUES
                        (:politician_id, :report_year, :total_assets, :total_real_estate,
                         :total_deposits, :total_securities, :total_crypto, :source)
                    ON CONFLICT (politician_id, report_year) DO UPDATE SET
                        total_assets = EXCLUDED.total_assets,
                        total_real_estate = EXCLUDED.total_real_estate,
                        total_deposits = EXCLUDED.total_deposits,
                        total_securities = EXCLUDED.total_securities,
                        total_crypto = EXCLUDED.total_crypto,
                        source = EXCLUDED.source
                """),
                {
                    "politician_id": pol_id,
                    "report_year": int(r["report_year"]),
                    "total_assets": _safe_int(r.get("total_assets", "")),
                    "total_real_estate": _safe_int(r.get("total_real_estate", "")),
                    "total_deposits": _safe_int(r.get("total_deposits", "")),
                    "total_securities": _safe_int(r.get("total_securities", "")),
                    "total_crypto": _safe_int(r.get("total_crypto", "")),
                    "source": r.get("source", "manual"),
                },
            )
            count += 1
        await session.commit()
    return count


@task(name="import-fund-rows")
async def import_fund_rows(rows: list[dict], database_url: str) -> int:
    """Upsert political fund rows."""
    session_factory = _get_session_factory(database_url)
    count = 0
    async with session_factory() as session:
        for r in rows:
            pol_id = r.get("politician_id")
            if not pol_id:
                continue
            await session.execute(
                text("""
                    INSERT INTO political_funds
                        (politician_id, fund_year, fund_type, income_total,
                         expense_total, balance, source)
                    VALUES
                        (:politician_id, :fund_year, :fund_type, :income_total,
                         :expense_total, :balance, :source)
                    ON CONFLICT (politician_id, fund_year, fund_type) DO UPDATE SET
                        income_total = EXCLUDED.income_total,
                        expense_total = EXCLUDED.expense_total,
                        balance = EXCLUDED.balance,
                        source = EXCLUDED.source
                """),
                {
                    "politician_id": pol_id,
                    "fund_year": int(r["fund_year"]),
                    "fund_type": r.get("fund_type", "후원회"),
                    "income_total": _safe_int(r.get("income_total", "")),
                    "expense_total": _safe_int(r.get("expense_total", "")),
                    "balance": _safe_int(r.get("balance", "")),
                    "source": r.get("source", "manual"),
                },
            )
            count += 1
        await session.commit()
    return count


@flow(name="import-assets", log_prints=True)
async def import_assets(
    csv_path: str,
    database_url: str | None = None,
) -> dict:
    """Import asset declarations from a CSV file.

    Args:
        csv_path: Path to assets CSV file.
        database_url: Database URL.

    Returns:
        Dict with import counts.
    """
    database_url = database_url or os.environ["DATABASE_URL"]
    path = Path(csv_path)

    if not path.exists():
        print(f"ERROR: File not found: {csv_path}")
        return {"imported": 0, "skipped": 0}

    rows: list[dict] = []
    skipped = 0

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("politician_name", "").strip()
            if not name:
                skipped += 1
                continue
            pol_id = await resolve_politician_id(name, database_url)
            if not pol_id:
                print(f"  Skipped: politician '{name}' not found")
                skipped += 1
                continue
            row["politician_id"] = pol_id
            rows.append(row)

    imported = await import_asset_rows(rows, database_url)
    print(f"Imported {imported} asset declarations, skipped {skipped}")
    return {"imported": imported, "skipped": skipped}


@flow(name="import-funds", log_prints=True)
async def import_funds(
    csv_path: str,
    database_url: str | None = None,
) -> dict:
    """Import political fund data from a CSV file.

    Args:
        csv_path: Path to funds CSV file.
        database_url: Database URL.

    Returns:
        Dict with import counts.
    """
    database_url = database_url or os.environ["DATABASE_URL"]
    path = Path(csv_path)

    if not path.exists():
        print(f"ERROR: File not found: {csv_path}")
        return {"imported": 0, "skipped": 0}

    rows: list[dict] = []
    skipped = 0

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("politician_name", "").strip()
            if not name:
                skipped += 1
                continue
            pol_id = await resolve_politician_id(name, database_url)
            if not pol_id:
                print(f"  Skipped: politician '{name}' not found")
                skipped += 1
                continue
            row["politician_id"] = pol_id
            rows.append(row)

    imported = await import_fund_rows(rows, database_url)
    print(f"Imported {imported} fund records, skipped {skipped}")
    return {"imported": imported, "skipped": skipped}


if __name__ == "__main__":
    import asyncio
    import sys

    if len(sys.argv) < 3:
        print("Usage: python import_assets.py <assets|funds> <csv_path>")
        sys.exit(1)

    mode = sys.argv[1]
    csv_file = sys.argv[2]

    if mode == "assets":
        asyncio.run(import_assets(csv_file))
    elif mode == "funds":
        asyncio.run(import_funds(csv_file))
    else:
        print(f"Unknown mode: {mode}. Use 'assets' or 'funds'.")
        sys.exit(1)

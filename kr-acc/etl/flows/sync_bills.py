"""Prefect flow: sync bill data and sponsors from 열린국회정보 API.

Large dataset with pagination. Includes sponsor string parsing to link
bills to politicians via the bill_sponsors table.
"""

import logging
import os

from prefect import flow

from tasks.extract import extract_bills
from tasks.load import load_bill_sponsors, load_bills
from tasks.transform import parse_sponsors, transform_bills
from tasks.validate import validate_bills

logger = logging.getLogger(__name__)


@flow(name="sync-bills", log_prints=True)
async def sync_bills(
    api_key: str | None = None,
    database_url: str | None = None,
    assembly_term: int = 22,
) -> dict:
    """Sync bill data and sponsor links.

    Args:
        api_key: Assembly API key.
        database_url: Database URL.
        assembly_term: Assembly term number.

    Returns:
        Dict with counts of synced records.
    """
    api_key = api_key or os.environ["ASSEMBLY_API_KEY"]
    database_url = database_url or os.environ["DATABASE_URL"]

    # Extract
    raw_bills = await extract_bills(api_key, assembly_term)

    # Transform
    bills = transform_bills(raw_bills, assembly_term)

    # Validate
    bills = validate_bills(bills)

    # Load bills
    bill_count = await load_bills(bills, database_url)

    # Parse and load sponsors
    sponsor_count = 0
    for bill in bills:
        sponsors = parse_sponsors(
            bill.get("_raw_proposer", ""),
            bill.get("_raw_rst_proposer", ""),
        )
        if sponsors:
            count = await load_bill_sponsors(bill["bill_id"], sponsors, database_url)
            sponsor_count += count

    print(f"Synced {bill_count} bills, {sponsor_count} sponsor links")
    return {
        "bills": bill_count,
        "sponsor_links": sponsor_count,
    }


if __name__ == "__main__":
    import asyncio

    asyncio.run(sync_bills())

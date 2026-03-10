"""Validate tasks — data quality checks before loading."""

import logging

from prefect import task

logger = logging.getLogger(__name__)


@task(name="validate-legislators")
def validate_legislators(records: list[dict]) -> list[dict]:
    """Validate legislator records, filtering out invalid ones."""
    valid = []
    for r in records:
        if not r.get("assembly_id"):
            logger.warning("Legislator missing assembly_id: %s", r.get("name"))
            continue
        if not r.get("name"):
            logger.warning("Legislator missing name: %s", r.get("assembly_id"))
            continue
        valid.append(r)
    if len(valid) < len(records):
        logger.warning(
            "Filtered %d/%d legislators (removed %d invalid)",
            len(valid), len(records), len(records) - len(valid),
        )
    return valid


@task(name="validate-bills")
def validate_bills(records: list[dict]) -> list[dict]:
    """Validate bill records."""
    valid = []
    for r in records:
        if not r.get("bill_id"):
            continue
        if not r.get("bill_name"):
            logger.warning("Bill missing name: %s", r.get("bill_id"))
            continue
        valid.append(r)
    if len(valid) < len(records):
        logger.warning(
            "Filtered %d/%d bills (removed %d invalid)",
            len(valid), len(records), len(records) - len(valid),
        )
    return valid


@task(name="validate-vote-summaries")
def validate_vote_summaries(records: list[dict]) -> list[dict]:
    """Validate vote summary records."""
    valid = []
    seen_ids: set[str] = set()
    for r in records:
        vid = r.get("vote_id")
        if not vid or vid in seen_ids:
            continue
        if not r.get("vote_date"):
            continue
        seen_ids.add(vid)
        valid.append(r)
    if len(valid) < len(records):
        logger.info(
            "Validated %d/%d vote summaries (%d duplicates/invalid removed)",
            len(valid), len(records), len(records) - len(valid),
        )
    return valid

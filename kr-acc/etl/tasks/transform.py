"""Transform tasks — clean and normalize raw API data."""

import logging
import re
from datetime import date

from prefect import task

from assembly_client import (
    RawBill,
    RawCommittee,
    RawLegislator,
    RawVotePerMember,
    RawVoteSummary,
)

logger = logging.getLogger(__name__)

# Regex to extract Korean names from proposer strings like "김철수의원 외 10인"
NAME_PATTERN = re.compile(r"([가-힣]{2,4})의원")

# Map Korean elected-count strings to integers
ELECTED_COUNT_MAP = {
    "초선": 1, "재선": 2, "3선": 3, "4선": 4, "5선": 5,
    "6선": 6, "7선": 7, "8선": 8, "9선": 9,
}


def _parse_date(date_str: str) -> date | None:
    """Parse date string in YYYYMMDD or YYYY-MM-DD format."""
    if not date_str or not date_str.strip():
        return None
    cleaned = date_str.strip().replace("-", "")
    if len(cleaned) == 8 and cleaned.isdigit():
        return date(int(cleaned[:4]), int(cleaned[4:6]), int(cleaned[6:8]))
    return None


def _safe_int(value: str | int | None) -> int | None:
    """Parse string or int to int, returning None on failure."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if not value or not value.strip():
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def _parse_elected_count(value: str) -> int | None:
    """Convert Korean elected-count string to integer."""
    if not value:
        return None
    return ELECTED_COUNT_MAP.get(value.strip())


def _parse_committees(cmits_str: str) -> list[str]:
    """Parse comma-separated committee string into a list."""
    if not cmits_str:
        return []
    return [c.strip() for c in cmits_str.split(",") if c.strip()]


@task(name="transform-legislators")
def transform_legislators(raw_rows: list[dict], assembly_term: int = 22) -> list[dict]:
    """Transform raw legislator API data into DB-ready dicts."""
    results = []
    for row in raw_rows:
        raw = RawLegislator.model_validate(row)
        if not raw.MONA_CD or not raw.HG_NM:
            logger.warning("Skipping legislator with missing ID or name: %s", row)
            continue
        results.append({
            "assembly_id": raw.MONA_CD,
            "name": raw.HG_NM,
            "name_hanja": raw.HJ_NM or None,
            "party": raw.POLY_NM or None,
            "constituency": raw.ORIG_NM or None,
            "elected_count": _parse_elected_count(raw.REELE_GBN_NM),
            "committees": _parse_committees(raw.CMITS),
            "profile_url": raw.LINK_URL or None,
            "photo_url": None,
            "eng_name": raw.ENG_NM or None,
            "bio": raw.MEM_TITLE or None,
            "email": raw.E_MAIL or None,
            "homepage": raw.HOMEPAGE or None,
            "office_address": raw.ASSEM_ADDR or None,
            "birth_date": _parse_date(raw.BTH_DATE),
            "gender": raw.SEX_GBN_NM or None,
            "assembly_term": assembly_term,
        })
    logger.info("Transformed %d/%d legislators", len(results), len(raw_rows))
    return results


@task(name="transform-bills")
def transform_bills(raw_rows: list[dict], assembly_term: int = 22) -> list[dict]:
    """Transform raw bill API data into DB-ready dicts."""
    results = []
    for row in raw_rows:
        raw = RawBill.model_validate(row)
        if not raw.BILL_ID:
            continue
        results.append({
            "bill_id": raw.BILL_ID,
            "bill_no": raw.BILL_NO or None,
            "bill_name": raw.BILL_NAME,
            "proposer_type": raw.PROPOSER_KIND or None,
            "propose_date": _parse_date(raw.PROPOSE_DT),
            "committee_id": raw.COMMITTEE_ID or None,
            "committee_name": raw.COMMITTEE or None,
            "status": None,
            "result": raw.PROC_RESULT or None,
            "assembly_term": assembly_term,
            "detail_url": raw.DETAIL_LINK or None,
            # Keep raw proposer for sponsor parsing
            "_raw_proposer": raw.PROPOSER,
            "_raw_rst_proposer": raw.RST_PROPOSER,
        })
    logger.info("Transformed %d/%d bills", len(results), len(raw_rows))
    return results


@task(name="parse-sponsors")
def parse_sponsors(proposer_str: str, primary_proposer: str = "") -> list[dict]:
    """Parse a proposer string into a list of sponsor entries.

    Args:
        proposer_str: Raw proposer string like "김철수의원(대표발의), 이영희의원, 박민수의원..."
        primary_proposer: Optional explicit primary proposer name.

    Returns:
        List of {"name": str, "sponsor_type": "primary"|"co-sponsor"} dicts.
    """
    if not proposer_str:
        return []

    names = NAME_PATTERN.findall(proposer_str)
    if not names:
        return []

    # Determine primary proposer
    primary_name = ""
    if primary_proposer:
        primary_match = NAME_PATTERN.search(primary_proposer)
        if primary_match:
            primary_name = primary_match.group(1)

    if not primary_name and "(대표발의)" in proposer_str:
        idx = proposer_str.index("(대표발의)")
        before = proposer_str[:idx]
        match = NAME_PATTERN.search(before)
        if match:
            primary_name = match.group(1)

    if not primary_name and names:
        primary_name = names[0]

    results = []
    seen = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        sponsor_type = "primary" if name == primary_name else "co-sponsor"
        results.append({"name": name, "sponsor_type": sponsor_type})

    return results


@task(name="transform-vote-summaries")
def transform_vote_summaries(raw_rows: list[dict], assembly_term: int = 22) -> list[dict]:
    """Transform raw vote summary data into DB-ready dicts."""
    results = []
    for row in raw_rows:
        raw = RawVoteSummary.model_validate(row)
        if not raw.BILL_ID or not raw.PROC_DT:
            continue
        vote_date = _parse_date(raw.PROC_DT)
        if not vote_date:
            continue
        # Generate a vote_id from bill_id + date
        vote_id = f"{raw.BILL_ID}_{raw.PROC_DT}"
        # Absent = total members - voters who showed up
        member_total = _safe_int(raw.MEMBER_TCNT)
        vote_total = _safe_int(raw.VOTE_TCNT)
        absent = (member_total - vote_total) if member_total and vote_total else None
        results.append({
            "vote_id": vote_id,
            "bill_id": raw.BILL_ID,
            "vote_date": vote_date,
            "total_members": member_total,
            "yes_count": _safe_int(raw.YES_TCNT),
            "no_count": _safe_int(raw.NO_TCNT),
            "abstain_count": _safe_int(raw.BLANK_TCNT),
            "absent_count": absent,
            "result": raw.PROC_RESULT_CD or None,
            "assembly_term": assembly_term,
        })
    logger.info("Transformed %d/%d vote summaries", len(results), len(raw_rows))
    return results


@task(name="transform-vote-members")
def transform_vote_members(raw_rows: list[dict], vote_id: str) -> list[dict]:
    """Transform per-member vote records into DB-ready dicts."""
    results = []
    for row in raw_rows:
        raw = RawVotePerMember.model_validate(row)
        if not raw.HG_NM:
            continue
        results.append({
            "vote_id": vote_id,
            "_politician_name": raw.HG_NM,
            "_party": raw.POLY_NM,
            "_constituency": raw.ORIG_NM,
            "vote_result": raw.RESULT_VOTE_MOD or None,
        })
    return results


@task(name="transform-committees")
def transform_committees(raw_rows: list[dict], assembly_term: int = 22) -> list[dict]:
    """Transform raw committee data into DB-ready dicts."""
    seen_ids: set[str] = set()
    results = []
    for row in raw_rows:
        raw = RawCommittee.model_validate(row)
        if not raw.CURR_COMMITTEE_ID or raw.CURR_COMMITTEE_ID in seen_ids:
            continue
        seen_ids.add(raw.CURR_COMMITTEE_ID)
        results.append({
            "committee_id": raw.CURR_COMMITTEE_ID,
            "name": raw.CURR_COMMITTEE,
            "committee_type": raw.COMMITTEE_TYPE or None,
            "assembly_term": assembly_term,
        })
    logger.info("Transformed %d unique committees", len(results))
    return results

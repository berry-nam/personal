"""Transform functions: convert raw API XML dicts to DB-ready dicts."""

import logging
import re
from datetime import date

from etl.config import ASSEMBLY_TERM

logger = logging.getLogger(__name__)


def _parse_date(s: str | None) -> str | None:
    """Parse date string from API (YYYY-MM-DD or YYYYMMDD)."""
    if not s:
        return None
    s = s.strip()
    if re.match(r"^\d{8}$", s):
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    return None


def _safe_int(s: str | None) -> int | None:
    """Parse an integer, returning None on failure."""
    if not s:
        return None
    try:
        return int(s.strip())
    except ValueError:
        return None


def transform_politicians(raw_rows: list[dict]) -> list[dict]:
    """Transform raw politician API data to DB-ready dicts."""
    results = []
    for row in raw_rows:
        results.append({
            "assembly_id": row.get("MONA_CD", "").strip(),
            "name": row.get("HG_NM", "").strip(),
            "name_hanja": row.get("HJ_NM", "").strip() or None,
            "party": row.get("POLY_NM", "").strip() or None,
            "constituency": row.get("ORIG_NM", "").strip() or None,
            "elected_count": _safe_int(row.get("REELE_GBN_NM", "").replace("선", "")),
            "profile_url": row.get("LINK_URL", "").strip() or None,
            "photo_url": row.get("JPIMG", "").strip() or None,
            "birth_date": _parse_date(row.get("BTH_DATE")),
            "gender": row.get("SEX_GBN_NM", "").strip() or None,
            "assembly_term": ASSEMBLY_TERM,
        })
    return [r for r in results if r["assembly_id"]]


def transform_bills(raw_rows: list[dict]) -> list[dict]:
    """Transform raw bill API data to DB-ready dicts."""
    results = []
    for row in raw_rows:
        bill_id = row.get("BILL_ID", "").strip()
        if not bill_id:
            continue
        results.append({
            "bill_id": bill_id,
            "bill_no": row.get("BILL_NO", "").strip() or None,
            "bill_name": row.get("BILL_NM", "").strip() or "",
            "proposer_type": row.get("PROPOSER_KIND", "").strip() or None,
            "propose_date": _parse_date(row.get("PROPOSE_DT")),
            "committee_id": row.get("COMMITTEE_ID", "").strip() or None,
            "committee_name": row.get("COMMITTEE", "").strip() or None,
            "status": row.get("PROC_RESULT", "").strip() or None,
            "result": row.get("PROC_RESULT", "").strip() or None,
            "assembly_term": ASSEMBLY_TERM,
            "detail_url": row.get("LINK_URL", "").strip() or None,
        })
    return results


def transform_votes(raw_rows: list[dict]) -> list[dict]:
    """Transform raw vote API data to DB-ready dicts."""
    results = []
    for row in raw_rows:
        vote_id = row.get("BILL_ID", "").strip()
        if not vote_id:
            continue
        results.append({
            "vote_id": vote_id,
            "bill_id": row.get("BILL_ID", "").strip(),
            "vote_date": _parse_date(row.get("VOTE_DATE")),
            "total_members": _safe_int(row.get("MEMBER_TCNT")),
            "yes_count": _safe_int(row.get("YES_TCNT")),
            "no_count": _safe_int(row.get("NO_TCNT")),
            "abstain_count": _safe_int(row.get("BLANK_TCNT")),
            "absent_count": _safe_int(row.get("ATTEND_TCNT")),
            "result": row.get("RESULT", "").strip() or None,
            "assembly_term": ASSEMBLY_TERM,
        })
    return results


def transform_vote_records(
    raw_rows: list[dict],
    vote_id: str,
    politician_id_map: dict[str, int],
) -> list[dict]:
    """Transform per-member vote records.

    Args:
        raw_rows: Raw API rows for one vote.
        vote_id: The vote ID these records belong to.
        politician_id_map: Mapping of politician name → DB id.
    """
    results = []
    for row in raw_rows:
        name = row.get("HG_NM", "").strip()
        pid = politician_id_map.get(name)
        if not pid:
            logger.debug("Could not find politician ID for: %s", name)
            continue

        result_text = row.get("RESULT_VOTE_MOD", "").strip()
        vote_result = {
            "찬성": "찬성",
            "반대": "반대",
            "기권": "기권",
        }.get(result_text, "불참")

        results.append({
            "vote_id": vote_id,
            "politician_id": pid,
            "vote_result": vote_result,
        })
    return results


def extract_unique_parties(politician_rows: list[dict]) -> list[dict]:
    """Extract unique party names from politician data."""
    parties = set()
    for row in politician_rows:
        party = row.get("party")
        if party:
            parties.add(party)
    return [{"name": p, "assembly_term": ASSEMBLY_TERM} for p in sorted(parties)]

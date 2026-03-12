"""HTTP client for 열린국회정보 REST API.

Handles XML→dict parsing, pagination, and retry logic.
"""

import logging
import xml.etree.ElementTree as ET

import httpx

from etl.config import ASSEMBLY_API_BASE, ASSEMBLY_API_KEY, ENDPOINTS, PAGE_SIZE

logger = logging.getLogger(__name__)


def _build_url(endpoint_key: str) -> str:
    """Build the full API URL for a given endpoint key."""
    code = ENDPOINTS[endpoint_key]
    return f"{ASSEMBLY_API_BASE}/{code}"


def _parse_xml_rows(xml_text: str, row_tag: str = "row") -> list[dict]:
    """Parse XML response into a list of dicts.

    열린국회정보 APIs return XML with <row> elements inside the result set.
    """
    root = ET.fromstring(xml_text)
    rows = []
    for row_el in root.iter(row_tag):
        item = {}
        for child in row_el:
            item[child.tag] = child.text
        rows.append(item)
    return rows


def _get_total_count(xml_text: str) -> int:
    """Extract total count from the API response header."""
    root = ET.fromstring(xml_text)
    for el in root.iter("list_total_count"):
        if el.text:
            return int(el.text)
    return 0


async def fetch_all_pages(
    endpoint_key: str,
    *,
    params: dict | None = None,
    row_tag: str = "row",
) -> list[dict]:
    """Fetch all pages from an 열린국회정보 API endpoint.

    Args:
        endpoint_key: Key from ENDPOINTS dict (e.g. 'politicians', 'bills').
        params: Additional query parameters.
        row_tag: XML tag name for individual rows.

    Returns:
        List of parsed row dicts from all pages.
    """
    url = _build_url(endpoint_key)
    base_params = {
        "KEY": ASSEMBLY_API_KEY,
        "Type": "xml",
        "pSize": PAGE_SIZE,
        **(params or {}),
    }

    all_rows: list[dict] = []
    page_index = 1

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            req_params = {**base_params, "pIndex": page_index}
            logger.info("Fetching %s page %d", endpoint_key, page_index)

            resp = await client.get(url, params=req_params)
            resp.raise_for_status()

            rows = _parse_xml_rows(resp.text, row_tag)
            if not rows:
                break

            all_rows.extend(rows)
            total = _get_total_count(resp.text)

            if len(all_rows) >= total or len(rows) < PAGE_SIZE:
                break

            page_index += 1

    logger.info("Fetched %d total rows from %s", len(all_rows), endpoint_key)
    return all_rows


async def fetch_single(
    endpoint_key: str,
    *,
    params: dict | None = None,
    row_tag: str = "row",
) -> list[dict]:
    """Fetch a single page from an API endpoint (no pagination)."""
    url = _build_url(endpoint_key)
    req_params = {
        "KEY": ASSEMBLY_API_KEY,
        "Type": "xml",
        "pSize": PAGE_SIZE,
        "pIndex": 1,
        **(params or {}),
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=req_params)
        resp.raise_for_status()
        return _parse_xml_rows(resp.text, row_tag)

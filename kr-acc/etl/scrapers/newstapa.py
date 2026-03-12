"""Newstapa 재산공개 (jaesan.newstapa.org) scraper.

Extracts politician asset declarations from Newstapa's public database.

Data flow:
1. Search by politician name via POST /get_list (phrase parameter)
2. Fetch detail page at /people/u/{hash}
3. Parse Chart.js data for yearly total assets
4. Parse per-year breakdown tables for category-level detail
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://jaesan.newstapa.org"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "X-Requested-With": "XMLHttpRequest",
}

# Parse Korean amount strings like "12억 1118만원", "4억 3718만원", "2033만원"
AMOUNT_PATTERN = re.compile(
    r"(?:(-?)(\d+)억\s*)?(?:(\d+)만)?원?"
)


@dataclass
class AssetBreakdown:
    """Single category within a year's asset declaration."""

    category: str
    percentage: str
    amount_text: str
    amount_krw: int | None = None


@dataclass
class YearlyAsset:
    """Asset declaration for a single year."""

    year: int
    total_assets: int | None = None
    breakdown: list[AssetBreakdown] = field(default_factory=list)


@dataclass
class NewstapaProfile:
    """Parsed Newstapa profile for a politician."""

    name: str
    details: str
    url_path: str
    yearly_assets: list[YearlyAsset] = field(default_factory=list)


def parse_korean_amount(text: str) -> int | None:
    """Parse Korean currency string to integer won.

    Examples:
        "12억 1118만원" -> 1_211_180_000
        "4억 3718만원" -> 437_180_000
        "2033만원" -> 20_330_000
        "-1억 2000만원" -> -120_000_000 (negative not common but handled)
    """
    if not text or text.strip() == "-":
        return None

    cleaned = text.strip().replace(",", "")
    total = 0

    # Try to extract 억 and 만
    eok_match = re.search(r"(\d+)억", cleaned)
    man_match = re.search(r"(\d+)만", cleaned)

    if eok_match:
        total += int(eok_match.group(1)) * 100_000_000
    if man_match:
        total += int(man_match.group(1)) * 10_000

    if not eok_match and not man_match:
        # Try plain number
        num_match = re.search(r"(\d+)", cleaned)
        if num_match:
            total = int(num_match.group(1))

    # Check for negative
    if cleaned.startswith("-") or "감소" in cleaned:
        total = -total

    return total if total != 0 or eok_match or man_match else None


def _parse_chart_data(html: str) -> list[YearlyAsset]:
    """Extract Chart.js labels (years) and data (total assets) from page HTML."""
    # Find all data arrays
    data_arrays = re.findall(r"data\s*:\s*\[([^\]]+)\]", html)
    if len(data_arrays) < 2:
        return []

    # data[0] = year labels (e.g. "2011년", "2012년", ...)
    # data[1] = total amounts in won
    labels = [v.strip().strip('"') for v in data_arrays[0].split(",")]
    amounts = [v.strip().strip('"') for v in data_arrays[1].split(",")]

    results = []
    for label, amount in zip(labels, amounts):
        year_match = re.search(r"(\d{4})", label)
        if not year_match:
            continue
        year = int(year_match.group(1))
        total = int(amount) if amount and amount != "-" else None
        results.append(YearlyAsset(year=year, total_assets=total))

    return results


def _parse_breakdown_tables(html: str) -> dict[int, list[AssetBreakdown]]:
    """Extract per-year breakdown tables from page HTML.

    Returns mapping of year -> list of AssetBreakdown items.
    """
    # Tables are associated with years. Pattern: "YYYY년" ... <table>...</table>
    year_tables = re.findall(
        r"(\d{4})년.*?<table[^>]*>(.*?)</table>", html, re.DOTALL
    )

    breakdowns: dict[int, list[AssetBreakdown]] = {}
    year_occurrence: dict[int, int] = {}  # track which occurrence of each year

    for year_str, table_html in year_tables:
        year = int(year_str)
        # Use first occurrence of each year only
        year_occurrence[year] = year_occurrence.get(year, 0) + 1
        if year_occurrence[year] > 1:
            continue

        rows = re.findall(r"<tr>(.*?)</tr>", table_html, re.DOTALL)
        items = []
        for row in rows:
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
            if len(cells) < 3:
                continue
            clean_cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            category, pct, amount_text = clean_cells[0], clean_cells[1], clean_cells[2]
            if not category or category == "항목":
                continue
            items.append(
                AssetBreakdown(
                    category=category,
                    percentage=pct,
                    amount_text=amount_text,
                    amount_krw=parse_korean_amount(amount_text),
                )
            )
        if items:
            breakdowns[year] = items

    return breakdowns


def parse_detail_page(html: str) -> list[YearlyAsset]:
    """Parse a Newstapa detail page into yearly asset data."""
    yearly = _parse_chart_data(html)
    breakdowns = _parse_breakdown_tables(html)

    for asset in yearly:
        if asset.year in breakdowns:
            asset.breakdown = breakdowns[asset.year]

    return yearly


class NewstapaScraper:
    """Async scraper for jaesan.newstapa.org."""

    def __init__(self, rate_limit: float = 2.0):
        self._min_interval = 1.0 / rate_limit
        self._last_request: float = 0.0

    async def _throttle(self) -> None:
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request = asyncio.get_event_loop().time()

    async def search(self, name: str, client: httpx.AsyncClient) -> list[dict]:
        """Search for a politician by name.

        Returns list of {"name": str, "details": str, "url": str}.
        """
        await self._throttle()
        resp = await client.post(
            f"{BASE_URL}/get_list",
            data={"phrase": name, "dataType": "json"},
            headers=DEFAULT_HEADERS,
        )
        resp.raise_for_status()
        results = resp.json()
        # Filter to exact name matches
        return [r for r in results if r.get("name") == name]

    async def fetch_profile(
        self, name: str, client: httpx.AsyncClient
    ) -> NewstapaProfile | None:
        """Search for a politician and fetch their asset profile.

        Returns NewstapaProfile or None if not found.
        """
        matches = await self.search(name, client)
        if not matches:
            logger.debug("No Newstapa match for: %s", name)
            return None

        match = matches[0]
        url_path = match["url"]

        await self._throttle()
        resp = await client.get(
            f"{BASE_URL}{url_path}",
            headers={"User-Agent": DEFAULT_HEADERS["User-Agent"]},
        )
        resp.raise_for_status()

        yearly = parse_detail_page(resp.text)

        return NewstapaProfile(
            name=match["name"],
            details=match.get("details", ""),
            url_path=url_path,
            yearly_assets=yearly,
        )

    async def fetch_profiles_batch(
        self, names: list[str], concurrency: int = 3
    ) -> dict[str, NewstapaProfile | None]:
        """Fetch profiles for multiple politicians with rate limiting.

        Args:
            names: List of politician names to look up.
            concurrency: Max concurrent profile fetches.

        Returns:
            Mapping of name -> NewstapaProfile (or None if not found).
        """
        results: dict[str, NewstapaProfile | None] = {}
        semaphore = asyncio.Semaphore(concurrency)

        async with httpx.AsyncClient(timeout=30) as client:
            async def _fetch(name: str) -> None:
                async with semaphore:
                    try:
                        results[name] = await self.fetch_profile(name, client)
                    except Exception:
                        logger.exception("Error fetching Newstapa profile for: %s", name)
                        results[name] = None

            tasks = [_fetch(name) for name in names]
            await asyncio.gather(*tasks)

        found = sum(1 for v in results.values() if v is not None)
        logger.info("Fetched %d/%d Newstapa profiles", found, len(names))
        return results

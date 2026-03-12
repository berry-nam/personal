"""LIKMS (likms.assembly.go.kr) per-member vote scraper.

Extracts individual legislator vote records from the LIKMS vote detail pages.
The Open Assembly API only provides vote summaries (yes/no/abstain counts),
not which member voted which way. LIKMS provides that per-member breakdown.

Data flow:
1. For each bill_id, fetch the LIKMS vote detail page
2. Parse the server-rendered HTML for voteAgreeList, voteDisAgreeList, voteAbsList
3. Extract member names from <p>name</p> tags within each list
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://likms.assembly.go.kr/bill/bi/bill/state/voteInfoDetailPage.do"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}

# Vote list IDs in the LIKMS page HTML
VOTE_LISTS = [
    ("voteAgreeList", "찬성"),
    ("voteDisAgreeList", "반대"),
    ("voteAbsList", "기권"),
]


@dataclass
class MemberVote:
    """A single member's vote on a bill."""

    name: str
    vote_result: str  # 찬성 | 반대 | 기권
    profile_url: str = ""


@dataclass
class BillVoteDetail:
    """Per-member vote breakdown for a bill."""

    bill_id: str
    member_votes: list[MemberVote] = field(default_factory=list)
    total_members: int = 0
    yes_count: int = 0
    no_count: int = 0
    abstain_count: int = 0


def parse_vote_page(html: str, bill_id: str) -> BillVoteDetail:
    """Parse a LIKMS vote detail page into per-member vote records.

    Args:
        html: Full HTML of the vote detail page.
        bill_id: The bill ID for reference.

    Returns:
        BillVoteDetail with all member votes extracted.
    """
    result = BillVoteDetail(bill_id=bill_id)
    counts = {"찬성": 0, "반대": 0, "기권": 0}

    for list_id, vote_type in VOTE_LISTS:
        start_idx = html.find(f'id="{list_id}"')
        if start_idx < 0:
            continue

        end_idx = html.find("</ul>", start_idx)
        if end_idx < 0:
            end_idx = start_idx + 100000

        section = html[start_idx:end_idx]

        # Extract member info from <li> elements
        lis = re.findall(r"<li[^>]*>(.*?)</li>", section, re.DOTALL)
        for li in lis:
            name_match = re.search(r"<p>([가-힣]{2,4})</p>", li)
            if not name_match:
                continue

            name = name_match.group(1)
            # Extract profile URL if available
            link_match = re.search(r'href="([^"]*assembly\.go\.kr[^"]*)"', li)
            profile_url = link_match.group(1) if link_match else ""

            result.member_votes.append(
                MemberVote(
                    name=name,
                    vote_result=vote_type,
                    profile_url=profile_url,
                )
            )
            counts[vote_type] += 1

    result.yes_count = counts["찬성"]
    result.no_count = counts["반대"]
    result.abstain_count = counts["기권"]

    # Try to extract total members from page summary
    total_match = re.search(r"재적\s*(\d+)", html)
    if total_match:
        result.total_members = int(total_match.group(1))

    return result


class LikmsScraper:
    """Async scraper for LIKMS per-member vote data."""

    def __init__(self, rate_limit: float = 2.0):
        self._min_interval = 1.0 / rate_limit
        self._last_request: float = 0.0

    async def _throttle(self) -> None:
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request = asyncio.get_event_loop().time()

    async def fetch_bill_votes(
        self, bill_id: str, client: httpx.AsyncClient
    ) -> BillVoteDetail | None:
        """Fetch per-member vote records for a single bill.

        Args:
            bill_id: The bill ID (e.g. PRC_D2H6F0Q2K0E5Y1S4I1M9Z5Q3J3Y3E5).
            client: httpx async client.

        Returns:
            BillVoteDetail or None if the page couldn't be fetched.
        """
        await self._throttle()
        try:
            resp = await client.get(
                BASE_URL,
                params={"billId": bill_id},
                headers=HEADERS,
                follow_redirects=True,
            )
            resp.raise_for_status()
            detail = parse_vote_page(resp.text, bill_id)
            if detail.member_votes:
                logger.info(
                    "Scraped %d member votes for bill %s (Y:%d N:%d A:%d)",
                    len(detail.member_votes),
                    bill_id,
                    detail.yes_count,
                    detail.no_count,
                    detail.abstain_count,
                )
            else:
                logger.debug("No member votes found for bill %s", bill_id)
                return None
            return detail
        except Exception:
            logger.exception("Error scraping LIKMS for bill %s", bill_id)
            return None

    async def fetch_bills_batch(
        self, bill_ids: list[str], concurrency: int = 3
    ) -> dict[str, BillVoteDetail | None]:
        """Fetch per-member votes for multiple bills.

        Args:
            bill_ids: List of bill IDs to scrape.
            concurrency: Max concurrent requests.

        Returns:
            Mapping of bill_id -> BillVoteDetail (or None).
        """
        results: dict[str, BillVoteDetail | None] = {}
        semaphore = asyncio.Semaphore(concurrency)

        async with httpx.AsyncClient(timeout=30) as client:

            async def _fetch(bid: str) -> None:
                async with semaphore:
                    results[bid] = await self.fetch_bill_votes(bid, client)

            tasks = [_fetch(bid) for bid in bill_ids]
            await asyncio.gather(*tasks)

        found = sum(1 for v in results.values() if v is not None)
        logger.info("Scraped %d/%d bills from LIKMS", found, len(bill_ids))
        return results

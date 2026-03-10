"""Async HTTP client for DART Open API (opendart.fss.or.kr).

Provides access to Korean corporate disclosure data including:
- Corporate info (기업개황)
- Executive roster (임원현황)
- Major shareholders (주요주주)
- Individual compensation (개인별 보수)
"""

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://opendart.fss.or.kr/api"

# Report codes
ANNUAL_REPORT = "11011"
SEMI_ANNUAL = "11012"
Q1_REPORT = "11013"
Q3_REPORT = "11014"


class DartAPIError(Exception):
    """Error from the DART API."""

    def __init__(self, message: str, status: str | None = None):
        super().__init__(message)
        self.status = status


class DartClient:
    """Async client for DART Open API.

    Args:
        api_key: DART API key from opendart.fss.or.kr.
        rate_limit: Max requests per second (default 5).
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        rate_limit: float = 5.0,
        timeout: float = 30,
    ):
        self.api_key = api_key
        self._min_interval = 1.0 / rate_limit
        self._last_request_time: float = 0.0
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "DartClient":
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _throttle(self) -> None:
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """Make a single DART API request."""
        url = f"{BASE_URL}/{endpoint}"
        query = {"crtfc_key": self.api_key, **params}

        client = self._client or httpx.AsyncClient(timeout=self.timeout)
        own_client = self._client is None

        try:
            await self._throttle()
            resp = await client.get(url, params=query)
            resp.raise_for_status()
            data = resp.json()

            status = data.get("status", "")
            if status not in ("000", "013"):
                # 000 = success, 013 = no data
                msg = data.get("message", "Unknown error")
                if status == "010":
                    raise DartAPIError(f"Invalid API key: {msg}", status=status)
                if status == "020":
                    raise DartAPIError(f"Rate limit exceeded: {msg}", status=status)
                raise DartAPIError(f"DART API error [{status}]: {msg}", status=status)

            return data
        finally:
            if own_client:
                await client.aclose()

    async def get_company(self, corp_code: str) -> dict[str, Any]:
        """Get company overview (기업개황).

        Returns: Company info dict with corp_name, ceo_nm, stock_code, industry_code, etc.
        """
        return await self._request("company.json", {"corp_code": corp_code})

    async def get_executives(
        self, corp_code: str, bsns_year: str, reprt_code: str = ANNUAL_REPORT
    ) -> list[dict[str, Any]]:
        """Get executive roster (임원현황).

        Returns: List of executive dicts with nm, sexdstn, birth_ym, ofcps, rgist_exctv_at, etc.
        """
        data = await self._request(
            "exctvSttus.json",
            {"corp_code": corp_code, "bsns_year": bsns_year, "reprt_code": reprt_code},
        )
        return data.get("list", [])

    async def get_major_shareholders(
        self, corp_code: str, bsns_year: str, reprt_code: str = ANNUAL_REPORT
    ) -> list[dict[str, Any]]:
        """Get major shareholders (주요주주).

        Returns: List with nm, relate, stock_knd, bsis_posesn_stock_co, etc.
        """
        data = await self._request(
            "majorstock.json",
            {"corp_code": corp_code, "bsns_year": bsns_year, "reprt_code": reprt_code},
        )
        return data.get("list", [])

    async def search_company(self, corp_name: str) -> list[dict[str, Any]]:
        """Search for a company by name. Note: DART doesn't have a direct search API.
        Use the corp_code list downloaded separately.

        This is a placeholder — in practice, you'd download the full corp_code XML
        from /api/corpCode.xml and build a local lookup table.
        """
        logger.warning("DART does not have a search API. Use corp_code list for lookups.")
        return []

"""Async HTTP client for 열린국회정보 (Open Assembly) API.

Features:
- Automatic retry with exponential backoff
- Rate limiting (requests per second)
- Auto-pagination to fetch all pages
- Structured error handling
"""

import asyncio
import logging
from typing import Any

import httpx

from .endpoints import BASE_URL

logger = logging.getLogger(__name__)

# Default rate limit: 5 requests/second (conservative for public API)
DEFAULT_RATE_LIMIT = 5.0
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30


class AssemblyAPIError(Exception):
    """Error from the Assembly API."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AssemblyClient:
    """Async client for 열린국회정보 API with retry, rate limiting, and pagination.

    Args:
        api_key: API key from open.assembly.go.kr.
        rate_limit: Max requests per second.
        max_retries: Max retry attempts on transient failures.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        rate_limit: float = DEFAULT_RATE_LIMIT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.timeout = timeout
        self._min_interval = 1.0 / rate_limit
        self._last_request_time: float = 0.0
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "AssemblyClient":
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": "Mozilla/5.0 (kr-acc ETL)"},
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _throttle(self) -> None:
        """Enforce rate limiting between requests."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
        page: int = 1,
        size: int = DEFAULT_PAGE_SIZE,
    ) -> tuple[list[dict[str, Any]], int]:
        """Make a single API request with retry.

        Args:
            endpoint: API endpoint slug.
            params: Additional query parameters.
            page: Page index (1-based).
            size: Page size.

        Returns:
            Tuple of (rows, total_count).

        Raises:
            AssemblyAPIError: On API or network errors after retries exhausted.
        """
        url = f"{BASE_URL}{endpoint}"
        query = {
            "KEY": self.api_key,
            "Type": "json",
            "pIndex": page,
            "pSize": size,
            **params,
        }

        client = self._client or httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": "Mozilla/5.0 (kr-acc ETL)"},
        )
        own_client = self._client is None

        try:
            for attempt in range(self.max_retries):
                await self._throttle()
                try:
                    resp = await client.get(url, params=query)
                    resp.raise_for_status()
                    data = resp.json()
                    return self._parse_response(data, endpoint)
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    if attempt == self.max_retries - 1:
                        raise AssemblyAPIError(
                            f"Network error after {self.max_retries} retries: {exc}"
                        ) from exc
                    wait = 2 ** (attempt + 1)
                    logger.warning(
                        "Retry %d/%d for %s (waiting %ds): %s",
                        attempt + 1,
                        self.max_retries,
                        endpoint,
                        wait,
                        exc,
                    )
                    await asyncio.sleep(wait)
                except httpx.HTTPStatusError as exc:
                    raise AssemblyAPIError(
                        f"HTTP {exc.response.status_code} from {endpoint}",
                        status_code=exc.response.status_code,
                    ) from exc
        finally:
            if own_client:
                await client.aclose()

        return [], 0  # unreachable, satisfies type checker

    @staticmethod
    def _parse_response(
        data: dict[str, Any], endpoint: str
    ) -> tuple[list[dict[str, Any]], int]:
        """Parse the Assembly API JSON response.

        Response structure: {endpoint_slug: [{head: [{list_total_count: N, ...}]}, {row: [...]}]}
        """
        container = data.get(endpoint, [])
        if not container:
            return [], 0

        # Extract total count from head
        total_count = 0
        if len(container) >= 1:
            head_list = container[0].get("head", [])
            for item in head_list:
                if "list_total_count" in item:
                    total_count = int(item["list_total_count"])
                    break

        # Extract rows
        rows: list[dict[str, Any]] = []
        if len(container) >= 2:
            rows = container[1].get("row", [])

        return rows, total_count

    async def fetch(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        page: int = 1,
        size: int = DEFAULT_PAGE_SIZE,
    ) -> list[dict[str, Any]]:
        """Fetch a single page of results.

        Args:
            endpoint: API endpoint slug.
            params: Additional query parameters.
            page: Page index (1-based).
            size: Page size (max 1000).

        Returns:
            List of row dicts.
        """
        params = params or {}
        rows, _ = await self._request(endpoint, params, page=page, size=size)
        return rows

    async def fetch_all(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        size: int = DEFAULT_PAGE_SIZE,
    ) -> list[dict[str, Any]]:
        """Fetch all pages of results via auto-pagination.

        Args:
            endpoint: API endpoint slug.
            params: Additional query parameters.
            size: Page size per request.

        Returns:
            All rows across all pages.
        """
        params = params or {}
        all_rows: list[dict[str, Any]] = []

        # First page — also gets total count
        rows, total_count = await self._request(endpoint, params, page=1, size=size)
        all_rows.extend(rows)

        if total_count <= size:
            return all_rows

        # Fetch remaining pages
        total_pages = (total_count + size - 1) // size
        logger.info(
            "Fetching %d total records across %d pages for %s",
            total_count,
            total_pages,
            endpoint,
        )

        for page in range(2, total_pages + 1):
            rows, _ = await self._request(endpoint, params, page=page, size=size)
            if not rows:
                break
            all_rows.extend(rows)

        return all_rows

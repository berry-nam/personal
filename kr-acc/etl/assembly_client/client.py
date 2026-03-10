"""Async HTTP client for 열린국회정보 API."""

import httpx

from .endpoints import BASE_URL


async def call_assembly_api(
    endpoint: str,
    params: dict,
    api_key: str,
    page: int = 1,
    size: int = 100,
) -> list[dict]:
    """Call an Open Assembly API endpoint and return rows.

    Args:
        endpoint: API endpoint slug.
        params: Additional query parameters.
        api_key: Assembly API key.
        page: Page index (1-based).
        size: Page size (max 1000).

    Returns:
        List of row dicts from the API response.
    """
    url = f"{BASE_URL}{endpoint}"
    query = {
        "KEY": api_key,
        "Type": "json",
        "pIndex": page,
        "pSize": size,
        **params,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=query)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get(endpoint, [{}])
        if len(rows) >= 2:
            return rows[1].get("row", [])
        return []

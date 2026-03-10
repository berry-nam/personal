"""Graph query service — Apache AGE co-sponsorship queries."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings


async def _init_age(session: AsyncSession) -> None:
    """Load AGE extension and set search path."""
    await session.execute(text("LOAD 'age'"))
    await session.execute(text("SET search_path = ag_catalog, \"$user\", public"))


def _escape(value: str) -> str:
    """Escape a string for Cypher queries."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


async def get_co_sponsorship_network(
    session: AsyncSession,
    *,
    party: str | None = None,
    min_weight: int = 3,
    limit: int = 500,
) -> dict:
    """Get co-sponsorship network data for D3.js force graph.

    Returns dict with 'nodes' and 'edges' lists.
    """
    graph = settings.age_graph_name
    await _init_age(session)

    # Get edges with optional party filter
    if party:
        escaped_party = _escape(party)
        cypher = f"""
            SELECT * FROM cypher('{graph}', $$
                MATCH (a:Politician)-[r:CO_SPONSORED]->(b:Politician)
                WHERE (a.party = '{escaped_party}' OR b.party = '{escaped_party}')
                  AND r.weight >= {min_weight}
                RETURN a.assembly_id, a.name, a.party,
                       b.assembly_id, b.name, b.party,
                       r.weight
                ORDER BY r.weight DESC
                LIMIT {limit}
            $$) AS (aid1 agtype, name1 agtype, party1 agtype,
                    aid2 agtype, name2 agtype, party2 agtype,
                    weight agtype)
        """
    else:
        cypher = f"""
            SELECT * FROM cypher('{graph}', $$
                MATCH (a:Politician)-[r:CO_SPONSORED]->(b:Politician)
                WHERE r.weight >= {min_weight}
                RETURN a.assembly_id, a.name, a.party,
                       b.assembly_id, b.name, b.party,
                       r.weight
                ORDER BY r.weight DESC
                LIMIT {limit}
            $$) AS (aid1 agtype, name1 agtype, party1 agtype,
                    aid2 agtype, name2 agtype, party2 agtype,
                    weight agtype)
        """

    result = await session.execute(text(cypher))
    rows = result.fetchall()

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    for row in rows:
        aid1, name1, party1, aid2, name2, party2, weight = (
            _strip_agtype(v) for v in row
        )
        nodes[aid1] = {"id": aid1, "name": name1, "party": party1, "group": party1}
        nodes[aid2] = {"id": aid2, "name": name2, "party": party2, "group": party2}
        edges.append({"source": aid1, "target": aid2, "weight": int(weight)})

    return {"nodes": list(nodes.values()), "edges": edges}


async def get_neighbors(
    session: AsyncSession,
    assembly_id: str,
    *,
    min_weight: int = 1,
    limit: int = 20,
) -> list[dict]:
    """Get co-sponsorship neighbors for a politician."""
    graph = settings.age_graph_name
    await _init_age(session)

    escaped_id = _escape(assembly_id)
    cypher = f"""
        SELECT * FROM cypher('{graph}', $$
            MATCH (a:Politician {{assembly_id: '{escaped_id}'}})-[r:CO_SPONSORED]-(b:Politician)
            WHERE r.weight >= {min_weight}
            RETURN b.assembly_id, b.name, b.party, r.weight
            ORDER BY r.weight DESC
            LIMIT {limit}
        $$) AS (aid agtype, name agtype, party agtype, weight agtype)
    """

    result = await session.execute(text(cypher))
    rows = result.fetchall()

    return [
        {
            "assembly_id": _strip_agtype(row[0]),
            "name": _strip_agtype(row[1]),
            "party": _strip_agtype(row[2]),
            "weight": int(_strip_agtype(row[3])),
        }
        for row in rows
    ]


def _strip_agtype(value) -> str:
    """Strip agtype wrapper quotes from AGE query results."""
    s = str(value)
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s

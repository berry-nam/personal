"""Load tasks — upsert data into PostgreSQL and sync to Apache AGE."""

import json
import logging
from typing import Any

from prefect import task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)


def _get_engine(database_url: str):
    """Create an async SQLAlchemy engine."""
    return create_async_engine(database_url, echo=False)


def _get_session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory."""
    engine = _get_engine(database_url)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@task(name="load-politicians")
async def load_politicians(records: list[dict], database_url: str) -> int:
    """Upsert politician records into the database.

    Returns:
        Number of records upserted.
    """
    if not records:
        return 0

    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        count = 0
        for r in records:
            await session.execute(
                text("""
                    INSERT INTO politicians
                        (assembly_id, name, name_hanja, party, constituency,
                         elected_count, committees, profile_url, photo_url,
                         birth_date, gender, assembly_term, updated_at)
                    VALUES
                        (:assembly_id, :name, :name_hanja, :party, :constituency,
                         :elected_count, CAST(:committees AS jsonb), :profile_url, :photo_url,
                         :birth_date, :gender, :assembly_term, NOW())
                    ON CONFLICT (assembly_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        name_hanja = EXCLUDED.name_hanja,
                        party = EXCLUDED.party,
                        constituency = EXCLUDED.constituency,
                        elected_count = EXCLUDED.elected_count,
                        committees = EXCLUDED.committees,
                        profile_url = EXCLUDED.profile_url,
                        birth_date = EXCLUDED.birth_date,
                        gender = EXCLUDED.gender,
                        updated_at = NOW()
                """),
                {
                    **r,
                    "committees": json.dumps(r["committees"]),
                },
            )
            count += 1
        await session.commit()
    logger.info("Upserted %d politicians", count)
    return count


@task(name="load-bills")
async def load_bills(records: list[dict], database_url: str) -> int:
    """Upsert bill records into the database.

    Returns:
        Number of records upserted.
    """
    if not records:
        return 0

    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        count = 0
        for r in records:
            # Strip internal fields before inserting
            db_record = {k: v for k, v in r.items() if not k.startswith("_")}
            await session.execute(
                text("""
                    INSERT INTO bills
                        (bill_id, bill_no, bill_name, proposer_type, propose_date,
                         committee_id, committee_name, status, result,
                         assembly_term, detail_url, updated_at)
                    VALUES
                        (:bill_id, :bill_no, :bill_name, :proposer_type, :propose_date,
                         :committee_id, :committee_name, :status, :result,
                         :assembly_term, :detail_url, NOW())
                    ON CONFLICT (bill_id) DO UPDATE SET
                        bill_name = EXCLUDED.bill_name,
                        proposer_type = EXCLUDED.proposer_type,
                        committee_id = EXCLUDED.committee_id,
                        committee_name = EXCLUDED.committee_name,
                        status = EXCLUDED.status,
                        result = EXCLUDED.result,
                        detail_url = EXCLUDED.detail_url,
                        updated_at = NOW()
                """),
                db_record,
            )
            count += 1
        await session.commit()
    logger.info("Upserted %d bills", count)
    return count


@task(name="load-bill-sponsors")
async def load_bill_sponsors(
    bill_id: str,
    sponsors: list[dict],
    database_url: str,
) -> int:
    """Upsert bill sponsor records. Matches sponsor names to politician IDs.

    Args:
        bill_id: The bill ID to link sponsors to.
        sponsors: List of {"name": str, "sponsor_type": str} dicts.
        database_url: Database connection URL.

    Returns:
        Number of sponsor links created.
    """
    if not sponsors:
        return 0

    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        count = 0
        for s in sponsors:
            # Look up politician by name
            result = await session.execute(
                text("SELECT id FROM politicians WHERE name = :name LIMIT 1"),
                {"name": s["name"]},
            )
            row = result.fetchone()
            if not row:
                continue
            politician_id = row[0]
            await session.execute(
                text("""
                    INSERT INTO bill_sponsors (bill_id, politician_id, sponsor_type)
                    VALUES (:bill_id, :politician_id, :sponsor_type)
                    ON CONFLICT (bill_id, politician_id) DO NOTHING
                """),
                {
                    "bill_id": bill_id,
                    "politician_id": politician_id,
                    "sponsor_type": s["sponsor_type"],
                },
            )
            count += 1
        await session.commit()
    return count


@task(name="load-vote-summaries")
async def load_vote_summaries(records: list[dict], database_url: str) -> int:
    """Upsert vote summary records.

    Returns:
        Number of records upserted.
    """
    if not records:
        return 0

    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        count = 0
        for r in records:
            # Check that the referenced bill exists
            bill_check = await session.execute(
                text("SELECT 1 FROM bills WHERE bill_id = :bill_id"),
                {"bill_id": r["bill_id"]},
            )
            if not bill_check.fetchone():
                logger.debug("Skipping vote for missing bill: %s", r["bill_id"])
                continue

            await session.execute(
                text("""
                    INSERT INTO votes
                        (vote_id, bill_id, vote_date, total_members, yes_count,
                         no_count, abstain_count, absent_count, result, assembly_term)
                    VALUES
                        (:vote_id, :bill_id, :vote_date, :total_members, :yes_count,
                         :no_count, :abstain_count, :absent_count, :result, :assembly_term)
                    ON CONFLICT (vote_id) DO UPDATE SET
                        total_members = EXCLUDED.total_members,
                        yes_count = EXCLUDED.yes_count,
                        no_count = EXCLUDED.no_count,
                        abstain_count = EXCLUDED.abstain_count,
                        absent_count = EXCLUDED.absent_count,
                        result = EXCLUDED.result
                """),
                r,
            )
            count += 1
        await session.commit()
    logger.info("Upserted %d vote summaries", count)
    return count


@task(name="load-vote-records")
async def load_vote_records(records: list[dict], database_url: str) -> int:
    """Upsert individual vote records (per-member).

    Records must have _politician_name for matching. Returns count upserted.
    """
    if not records:
        return 0

    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        count = 0
        for r in records:
            # Look up politician by name (and optionally party/constituency for disambiguation)
            result = await session.execute(
                text("SELECT id FROM politicians WHERE name = :name LIMIT 1"),
                {"name": r["_politician_name"]},
            )
            row = result.fetchone()
            if not row:
                continue
            politician_id = row[0]
            await session.execute(
                text("""
                    INSERT INTO vote_records (vote_id, politician_id, vote_result)
                    VALUES (:vote_id, :politician_id, :vote_result)
                    ON CONFLICT (vote_id, politician_id) DO UPDATE SET
                        vote_result = EXCLUDED.vote_result
                """),
                {
                    "vote_id": r["vote_id"],
                    "politician_id": politician_id,
                    "vote_result": r["vote_result"],
                },
            )
            count += 1
        await session.commit()
    return count


@task(name="load-committees")
async def load_committees(records: list[dict], database_url: str) -> int:
    """Upsert committee records."""
    if not records:
        return 0

    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        count = 0
        for r in records:
            await session.execute(
                text("""
                    INSERT INTO committees (committee_id, name, committee_type, assembly_term)
                    VALUES (:committee_id, :name, :committee_type, :assembly_term)
                    ON CONFLICT (committee_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        committee_type = EXCLUDED.committee_type
                """),
                r,
            )
            count += 1
        await session.commit()
    logger.info("Upserted %d committees", count)
    return count


@task(name="sync-age-politicians")
async def sync_age_politicians(database_url: str, graph_name: str = "kr_acc") -> int:
    """Sync politician nodes to Apache AGE graph."""
    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        # Load AGE and set search path
        await session.execute(text("LOAD 'age'"))
        await session.execute(text("SET search_path = ag_catalog, \"$user\", public"))

        # Get all politicians
        result = await session.execute(
            text("SELECT id, assembly_id, name, party FROM politicians")
        )
        politicians = result.fetchall()

        count = 0
        for p in politicians:
            pid, assembly_id, name, party = p
            # Merge politician node
            cypher = f"""
                SELECT * FROM cypher('{graph_name}', $$
                    MERGE (p:Politician {{assembly_id: '{assembly_id}'}})
                    SET p.name = '{_escape_cypher(name)}',
                        p.party = '{_escape_cypher(party or "")}',
                        p.db_id = {pid}
                    RETURN p
                $$) AS (v agtype)
            """
            await session.execute(text(cypher))
            count += 1

        # Sync party nodes
        party_result = await session.execute(
            text("SELECT name, color_hex FROM parties")
        )
        for party_name, color_hex in party_result.fetchall():
            cypher = f"""
                SELECT * FROM cypher('{graph_name}', $$
                    MERGE (p:Party {{name: '{_escape_cypher(party_name)}'}})
                    SET p.color = '{color_hex or ""}'
                    RETURN p
                $$) AS (v agtype)
            """
            await session.execute(text(cypher))

        # Create MEMBER_OF edges (politician -> party)
        for p in politicians:
            pid, assembly_id, name, party = p
            if not party:
                continue
            cypher = f"""
                SELECT * FROM cypher('{graph_name}', $$
                    MATCH (pol:Politician {{assembly_id: '{assembly_id}'}}),
                          (par:Party {{name: '{_escape_cypher(party)}'}})
                    MERGE (pol)-[:MEMBER_OF]->(par)
                    RETURN pol
                $$) AS (v agtype)
            """
            await session.execute(text(cypher))

        await session.commit()
    logger.info("Synced %d politicians to AGE graph", count)
    return count


@task(name="sync-age-co-sponsorship")
async def sync_age_co_sponsorship(
    database_url: str, graph_name: str = "kr_acc"
) -> int:
    """Compute and sync co-sponsorship edges to AGE graph.

    Creates CO_SPONSORED edges between politicians who co-sponsor bills together,
    weighted by the number of shared bills.
    """
    session_factory = _get_session_factory(database_url)
    async with session_factory() as session:
        await session.execute(text("LOAD 'age'"))
        await session.execute(text("SET search_path = ag_catalog, \"$user\", public"))

        # Compute co-sponsorship pairs with counts
        result = await session.execute(text("""
            SELECT
                p1.assembly_id AS aid1,
                p2.assembly_id AS aid2,
                COUNT(*) AS shared_bills
            FROM bill_sponsors bs1
            JOIN bill_sponsors bs2
                ON bs1.bill_id = bs2.bill_id
                AND bs1.politician_id < bs2.politician_id
            JOIN politicians p1 ON bs1.politician_id = p1.id
            JOIN politicians p2 ON bs2.politician_id = p2.id
            GROUP BY p1.assembly_id, p2.assembly_id
            HAVING COUNT(*) >= 3
        """))
        pairs = result.fetchall()

        count = 0
        for aid1, aid2, shared_bills in pairs:
            cypher = f"""
                SELECT * FROM cypher('{graph_name}', $$
                    MATCH (a:Politician {{assembly_id: '{aid1}'}}),
                          (b:Politician {{assembly_id: '{aid2}'}})
                    MERGE (a)-[r:CO_SPONSORED]->(b)
                    SET r.weight = {shared_bills}
                    RETURN r
                $$) AS (e agtype)
            """
            await session.execute(text(cypher))
            count += 1

        await session.commit()
    logger.info("Synced %d co-sponsorship edges to AGE graph", count)
    return count


def _escape_cypher(value: str) -> str:
    """Escape a string for safe use in Cypher queries."""
    return value.replace("\\", "\\\\").replace("'", "\\'")

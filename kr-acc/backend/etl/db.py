"""Synchronous database helpers for ETL pipeline.

Uses psycopg2 directly for bulk upserts and AGE graph operations.
"""

import logging

import psycopg2
import psycopg2.extras

from etl.config import AGE_GRAPH_NAME, DATABASE_URL_SYNC

logger = logging.getLogger(__name__)


def get_connection():
    """Get a psycopg2 connection."""
    return psycopg2.connect(DATABASE_URL_SYNC)


def upsert_politicians(rows: list[dict]) -> int:
    """Upsert politician rows into the politicians table.

    Returns the number of rows upserted.
    """
    if not rows:
        return 0

    sql = """
        INSERT INTO politicians (assembly_id, name, name_hanja, party, constituency,
                                 elected_count, profile_url, photo_url, birth_date,
                                 gender, assembly_term, updated_at)
        VALUES (%(assembly_id)s, %(name)s, %(name_hanja)s, %(party)s, %(constituency)s,
                %(elected_count)s, %(profile_url)s, %(photo_url)s, %(birth_date)s,
                %(gender)s, %(assembly_term)s, NOW())
        ON CONFLICT (assembly_id) DO UPDATE SET
            name = EXCLUDED.name,
            name_hanja = EXCLUDED.name_hanja,
            party = EXCLUDED.party,
            constituency = EXCLUDED.constituency,
            elected_count = EXCLUDED.elected_count,
            profile_url = EXCLUDED.profile_url,
            photo_url = EXCLUDED.photo_url,
            birth_date = EXCLUDED.birth_date,
            gender = EXCLUDED.gender,
            updated_at = NOW()
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, sql, rows, page_size=100)
        conn.commit()
        logger.info("Upserted %d politicians", len(rows))
        return len(rows)
    finally:
        conn.close()


def upsert_bills(rows: list[dict]) -> int:
    """Upsert bill rows into the bills table."""
    if not rows:
        return 0

    sql = """
        INSERT INTO bills (bill_id, bill_no, bill_name, proposer_type, propose_date,
                          committee_id, committee_name, status, result, assembly_term,
                          detail_url, updated_at)
        VALUES (%(bill_id)s, %(bill_no)s, %(bill_name)s, %(proposer_type)s, %(propose_date)s,
                %(committee_id)s, %(committee_name)s, %(status)s, %(result)s, %(assembly_term)s,
                %(detail_url)s, NOW())
        ON CONFLICT (bill_id) DO UPDATE SET
            bill_name = EXCLUDED.bill_name,
            status = EXCLUDED.status,
            result = EXCLUDED.result,
            committee_name = EXCLUDED.committee_name,
            detail_url = EXCLUDED.detail_url,
            updated_at = NOW()
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, sql, rows, page_size=100)
        conn.commit()
        logger.info("Upserted %d bills", len(rows))
        return len(rows)
    finally:
        conn.close()


def upsert_votes(rows: list[dict]) -> int:
    """Upsert vote rows into the votes table."""
    if not rows:
        return 0

    sql = """
        INSERT INTO votes (vote_id, bill_id, vote_date, total_members,
                          yes_count, no_count, abstain_count, absent_count,
                          result, assembly_term)
        VALUES (%(vote_id)s, %(bill_id)s, %(vote_date)s, %(total_members)s,
                %(yes_count)s, %(no_count)s, %(abstain_count)s, %(absent_count)s,
                %(result)s, %(assembly_term)s)
        ON CONFLICT (vote_id) DO UPDATE SET
            result = EXCLUDED.result,
            yes_count = EXCLUDED.yes_count,
            no_count = EXCLUDED.no_count,
            abstain_count = EXCLUDED.abstain_count,
            absent_count = EXCLUDED.absent_count
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, sql, rows, page_size=100)
        conn.commit()
        logger.info("Upserted %d votes", len(rows))
        return len(rows)
    finally:
        conn.close()


def upsert_vote_records(rows: list[dict]) -> int:
    """Upsert individual vote records."""
    if not rows:
        return 0

    sql = """
        INSERT INTO vote_records (vote_id, politician_id, vote_result)
        VALUES (%(vote_id)s, %(politician_id)s, %(vote_result)s)
        ON CONFLICT (vote_id, politician_id) DO UPDATE SET
            vote_result = EXCLUDED.vote_result
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, sql, rows, page_size=500)
        conn.commit()
        logger.info("Upserted %d vote records", len(rows))
        return len(rows)
    finally:
        conn.close()


def upsert_bill_sponsors(rows: list[dict]) -> int:
    """Upsert bill sponsor entries."""
    if not rows:
        return 0

    sql = """
        INSERT INTO bill_sponsors (bill_id, politician_id, sponsor_type)
        VALUES (%(bill_id)s, %(politician_id)s, %(sponsor_type)s)
        ON CONFLICT (bill_id, politician_id) DO NOTHING
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, sql, rows, page_size=500)
        conn.commit()
        logger.info("Upserted %d bill sponsors", len(rows))
        return len(rows)
    finally:
        conn.close()


def upsert_parties(rows: list[dict]) -> int:
    """Upsert party entries."""
    if not rows:
        return 0

    sql = """
        INSERT INTO parties (name, assembly_term)
        VALUES (%(name)s, %(assembly_term)s)
        ON CONFLICT (name) DO NOTHING
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, sql, rows, page_size=50)
        conn.commit()
        return len(rows)
    finally:
        conn.close()


def get_politician_id_map() -> dict[str, int]:
    """Get mapping of assembly_id → politician DB id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT assembly_id, id FROM politicians")
            return {row[0]: row[1] for row in cur.fetchall()}
    finally:
        conn.close()


def sync_age_politicians() -> None:
    """Sync Politician nodes to the AGE graph layer."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("LOAD 'age'")
            cur.execute("SET search_path = ag_catalog, \"$user\", public")

            # Ensure graph exists
            cur.execute(
                "SELECT count(*) FROM ag_graph WHERE name = %s", (AGE_GRAPH_NAME,)
            )
            if cur.fetchone()[0] == 0:
                cur.execute(f"SELECT create_graph('{AGE_GRAPH_NAME}')")

            # Merge politician nodes from relational table
            cur.execute(f"""
                SELECT * FROM cypher('{AGE_GRAPH_NAME}', $$
                    MATCH (p:Politician)
                    DETACH DELETE p
                $$) AS (result agtype)
            """)

            cur.execute("""
                SELECT assembly_id, name, party, constituency, assembly_term
                FROM politicians
            """)
            for row in cur.fetchall():
                aid, name, party, const, term = row
                safe = lambda s: (s or "").replace("'", "\\'")
                cur.execute(f"""
                    SELECT * FROM cypher('{AGE_GRAPH_NAME}', $$
                        CREATE (:Politician {{
                            assembly_id: '{safe(aid)}',
                            name: '{safe(name)}',
                            party: '{safe(party)}',
                            constituency: '{safe(const)}',
                            assembly_term: {term}
                        }})
                    $$) AS (result agtype)
                """)

        conn.commit()
        logger.info("Synced Politician nodes to AGE graph")
    finally:
        conn.close()


def compute_co_sponsorship_edges() -> int:
    """Compute CO_SPONSORED edges from bill_sponsors table.

    Creates weighted edges between politicians who co-sponsor the same bills.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("LOAD 'age'")
            cur.execute("SET search_path = ag_catalog, \"$user\", public")

            # Clear existing CO_SPONSORED edges
            cur.execute(f"""
                SELECT * FROM cypher('{AGE_GRAPH_NAME}', $$
                    MATCH ()-[r:CO_SPONSORED]->()
                    DELETE r
                $$) AS (result agtype)
            """)

            # Compute co-sponsorship pairs with counts
            cur.execute("""
                SELECT a.assembly_id, b.assembly_id, COUNT(DISTINCT s1.bill_id) as cnt
                FROM bill_sponsors s1
                JOIN bill_sponsors s2 ON s1.bill_id = s2.bill_id
                    AND s1.politician_id < s2.politician_id
                JOIN politicians a ON s1.politician_id = a.id
                JOIN politicians b ON s2.politician_id = b.id
                GROUP BY a.assembly_id, b.assembly_id
                HAVING COUNT(DISTINCT s1.bill_id) >= 3
            """)
            pairs = cur.fetchall()

            for aid1, aid2, count in pairs:
                safe = lambda s: (s or "").replace("'", "\\'")
                cur.execute(f"""
                    SELECT * FROM cypher('{AGE_GRAPH_NAME}', $$
                        MATCH (a:Politician {{assembly_id: '{safe(aid1)}'}}),
                              (b:Politician {{assembly_id: '{safe(aid2)}'}})
                        CREATE (a)-[:CO_SPONSORED {{weight: {count}}}]->(b)
                    $$) AS (result agtype)
                """)

        conn.commit()
        logger.info("Created %d co-sponsorship edges", len(pairs))
        return len(pairs)
    finally:
        conn.close()

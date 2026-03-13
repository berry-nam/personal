"""Graph API endpoints — co-sponsorship network queries via Apache AGE."""

from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import (
    AssetDeclaration,
    Bill,
    BillSponsor,
    Company,
    Politician,
    PoliticianCompany,
    Vote,
)
from app.schemas.schemas import GraphData, NeighborOut
from app.services import graph_service

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/co-sponsorship", response_model=GraphData)
async def get_co_sponsorship_network(
    party: str | None = None,
    min_weight: int = Query(3, ge=1),
    limit: int = Query(500, ge=1, le=5000),
    session: AsyncSession = Depends(get_session),
):
    """Get co-sponsorship network data for visualization.

    Returns nodes and edges suitable for D3.js force-directed graph.
    """
    data = await graph_service.get_co_sponsorship_network(
        session, party=party, min_weight=min_weight, limit=limit
    )
    return GraphData(**data)


@router.get("/neighbors/{assembly_id}", response_model=list[NeighborOut])
async def get_neighbors(
    assembly_id: str,
    min_weight: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Get co-sponsorship neighbors for a specific politician."""
    neighbors = await graph_service.get_neighbors(
        session, assembly_id, min_weight=min_weight, limit=limit
    )
    return [NeighborOut(**n) for n in neighbors]


@router.get("/unified")
async def get_unified_graph(
    assembly_term: int = Query(22),
    min_cosponsorship: int = Query(5, ge=1),
    cosponsorship_limit: int = Query(400, ge=1, le=3000),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Unified relationship graph: politicians + companies + votes + assets.

    Node types: politician, company, vote, asset
    Edge types: co_sponsored, related_company, voted_on, owns_asset
    """
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    # 1) Politicians as central nodes
    pol_result = await session.execute(
        select(
            Politician.id,
            Politician.assembly_id,
            Politician.name,
            Politician.party,
            Politician.photo_url,
        ).where(Politician.assembly_term == assembly_term)
    )
    pol_rows = pol_result.all()
    pol_id_to_aid: dict[int, str] = {}
    for row in pol_rows:
        nid = f"pol_{row.assembly_id}"
        pol_id_to_aid[row.id] = nid
        nodes[nid] = {
            "id": nid,
            "name": row.name,
            "party": row.party,
            "group": "politician",
            "node_type": "politician",
            "photo_url": row.photo_url,
        }

    # 2) Co-sponsorship edges (from relational data — BillSponsor pairs)
    # Find pairs of politicians who co-sponsored the same bills
    bs1 = select(
        BillSponsor.bill_id, BillSponsor.politician_id
    ).subquery("bs1")
    bs2 = select(
        BillSponsor.bill_id, BillSponsor.politician_id
    ).subquery("bs2")

    cosponsor_result = await session.execute(
        select(
            bs1.c.politician_id.label("pid1"),
            bs2.c.politician_id.label("pid2"),
            func.count().label("weight"),
        )
        .select_from(bs1)
        .join(bs2, (bs1.c.bill_id == bs2.c.bill_id) & (bs1.c.politician_id < bs2.c.politician_id))
        .where(
            bs1.c.politician_id.in_(select(Politician.id).where(Politician.assembly_term == assembly_term)),
            bs2.c.politician_id.in_(select(Politician.id).where(Politician.assembly_term == assembly_term)),
        )
        .group_by(bs1.c.politician_id, bs2.c.politician_id)
        .having(func.count() >= min_cosponsorship)
        .order_by(func.count().desc())
        .limit(cosponsorship_limit)
    )
    for row in cosponsor_result.all():
        src = pol_id_to_aid.get(row.pid1)
        tgt = pol_id_to_aid.get(row.pid2)
        if src and tgt:
            edges.append({
                "source": src,
                "target": tgt,
                "weight": row.weight,
                "edge_type": "co_sponsored",
            })

    # 3) Company connections
    company_result = await session.execute(
        select(
            PoliticianCompany.politician_id,
            PoliticianCompany.relation_type,
            Company.id.label("company_id"),
            Company.corp_code,
            Company.corp_name,
            Company.industry,
        )
        .join(Company, Company.id == PoliticianCompany.company_id)
        .where(
            PoliticianCompany.politician_id.in_(
                select(Politician.id).where(Politician.assembly_term == assembly_term)
            )
        )
    )
    for row in company_result.all():
        cid = f"company_{row.company_id}"
        if cid not in nodes:
            nodes[cid] = {
                "id": cid,
                "name": row.corp_name,
                "party": None,
                "group": "company",
                "node_type": "company",
                "industry": row.industry,
            }
        pol_nid = pol_id_to_aid.get(row.politician_id)
        if pol_nid:
            edges.append({
                "source": pol_nid,
                "target": cid,
                "weight": 2,
                "edge_type": "related_company",
                "label": row.relation_type,
            })

    # 4) Asset nodes — top asset holders become visible nodes
    asset_result = await session.execute(
        select(
            AssetDeclaration.politician_id,
            AssetDeclaration.total_assets,
            AssetDeclaration.total_real_estate,
            AssetDeclaration.total_securities,
            AssetDeclaration.total_crypto,
            AssetDeclaration.report_year,
        )
        .where(
            AssetDeclaration.politician_id.in_(
                select(Politician.id).where(Politician.assembly_term == assembly_term)
            )
        )
        .order_by(AssetDeclaration.total_assets.desc())
        .limit(30)
    )
    for row in asset_result.all():
        aid = f"asset_{row.politician_id}_{row.report_year}"
        label_parts = []
        if row.total_real_estate and row.total_real_estate > 0:
            label_parts.append("부동산")
        if row.total_securities and row.total_securities > 0:
            label_parts.append("유가증권")
        if row.total_crypto and row.total_crypto > 0:
            label_parts.append("가상자산")
        nodes[aid] = {
            "id": aid,
            "name": f"재산 {row.report_year}" + (f" ({', '.join(label_parts)})" if label_parts else ""),
            "party": None,
            "group": "asset",
            "node_type": "asset",
            "total_assets": row.total_assets,
        }
        pol_nid = pol_id_to_aid.get(row.politician_id)
        if pol_nid:
            edges.append({
                "source": pol_nid,
                "target": aid,
                "weight": 1,
                "edge_type": "owns_asset",
            })

    # 5) Controversial vote nodes (top 10 most opposed)
    vote_result = await session.execute(
        select(
            Vote.vote_id,
            Vote.bill_id,
            Vote.vote_date,
            Vote.yes_count,
            Vote.no_count,
            Vote.total_members,
            Vote.result,
            Bill.bill_name,
        )
        .join(Bill, Bill.bill_id == Vote.bill_id)
        .where(
            Vote.assembly_term == assembly_term,
            Vote.total_members > 0,
            Vote.no_count > 0,
        )
        .order_by((Vote.no_count * 1.0 / Vote.total_members).desc())
        .limit(10)
    )
    vote_rows = vote_result.all()
    vote_bill_map: dict[str, str] = {}
    for row in vote_rows:
        vid = f"vote_{row.vote_id}"
        nodes[vid] = {
            "id": vid,
            "name": row.bill_name or row.bill_id,
            "party": None,
            "group": "vote",
            "node_type": "vote",
            "result": row.result,
            "yes_count": row.yes_count,
            "no_count": row.no_count,
        }
        vote_bill_map[row.bill_id] = vid

    if vote_bill_map:
        sponsor_result = await session.execute(
            select(BillSponsor.bill_id, BillSponsor.politician_id)
            .where(
                BillSponsor.bill_id.in_(list(vote_bill_map.keys())),
                BillSponsor.sponsor_type == "primary",
                BillSponsor.politician_id.in_(
                    select(Politician.id).where(Politician.assembly_term == assembly_term)
                ),
            )
        )
        for row in sponsor_result.all():
            pol_nid = pol_id_to_aid.get(row.politician_id)
            vid = vote_bill_map.get(row.bill_id)
            if pol_nid and vid:
                edges.append({
                    "source": pol_nid,
                    "target": vid,
                    "weight": 3,
                    "edge_type": "sponsored_vote",
                })

    return {"nodes": list(nodes.values()), "edges": edges}

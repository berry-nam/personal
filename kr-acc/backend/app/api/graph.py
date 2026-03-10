"""Graph API endpoints — co-sponsorship network queries via Apache AGE."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
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

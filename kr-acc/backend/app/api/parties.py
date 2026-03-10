"""Party and committee reference data endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Committee, Party
from app.schemas.schemas import CommitteeOut, PartyOut

router = APIRouter(tags=["reference"])


@router.get("/parties", response_model=list[PartyOut])
async def list_parties(
    assembly_term: int = 22,
    session: AsyncSession = Depends(get_session),
):
    """List all parties for the given assembly term."""
    result = await session.execute(
        select(Party).where(Party.assembly_term == assembly_term).order_by(Party.name)
    )
    return [PartyOut.model_validate(p) for p in result.scalars().all()]


@router.get("/committees", response_model=list[CommitteeOut])
async def list_committees(
    assembly_term: int = 22,
    session: AsyncSession = Depends(get_session),
):
    """List all committees for the given assembly term."""
    result = await session.execute(
        select(Committee)
        .where(Committee.assembly_term == assembly_term)
        .order_by(Committee.name)
    )
    return [CommitteeOut.model_validate(c) for c in result.scalars().all()]

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import select
from pydantic import BaseModel

from icon_stats.db import get_session
from icon_stats.models.exchanges_legacy import ExchangesLegacy

router = APIRouter()


class ExchangesLegacyResponse(BaseModel):
    result: int = 200
    description: str = ""
    totalData: int | None = None
    data: dict


@router.get("/stats/exchanges/legacy")
async def get_exchange_prices(
        response: Response,
        session: AsyncSession = Depends(get_session),
) -> list[ExchangesLegacyResponse]:
    """Return list of delegations."""
    query = (
        select(ExchangesLegacy)
    )

    result = await session.execute(query)
    data = result.scalars().all()

    exchanges_legacy = ExchangesLegacyResponse(
        data=data,
    )

    return exchanges_legacy

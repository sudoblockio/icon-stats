from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import select
from pydantic import BaseModel
from datetime import datetime

from icon_stats.db import get_session_api
from icon_stats.models.cmc_cryptocurrency_quotes_latest import CmcListingsLatestQuote

router = APIRouter()


class ExchangesLegacyResponseData(BaseModel):
    marketName: str
    tradeName: str
    createDate: datetime
    price: float
    prePrice: float
    dailyRate: float | None
    volume: float
    marketCap: float


class ExchangesLegacyResponse(BaseModel):
    result: int = 200
    description: str = ""
    totalData: int | None = None
    data: ExchangesLegacyResponseData


@router.get("/stats/exchanges/legacy", response_model=ExchangesLegacyResponse)
async def get_exchange_prices(
        session: AsyncSession = Depends(get_session_api),
) -> ExchangesLegacyResponse:
    """Return list of delegations."""
    query = (
        select(CmcListingsLatestQuote)
        .where(CmcListingsLatestQuote.base == "ICX")  # noqa
        .order_by(CmcListingsLatestQuote.last_updated.desc())
        .limit(1)
    )

    result = await session.execute(query)
    data = result.scalars().first()

    if not data:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)  # Raise an HTTPException for the 204 status

    exchanges_legacy_response_data = ExchangesLegacyResponseData(
        marketName="coinmarketcap",
        tradeName="icxusd",
        createDate=data.last_updated,
        price=data.price,
        prePrice=data.price + (data.price * data.percent_change_24h / 100),
        dailyRate=None,
        volume=data.volume_24h,
        marketCap=data.market_cap,
    )
    exchanges_legacy = ExchangesLegacyResponse(
        data=exchanges_legacy_response_data,
    )

    return exchanges_legacy

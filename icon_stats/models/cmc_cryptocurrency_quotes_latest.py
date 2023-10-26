import datetime

from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel


class CmcListingsLatestQuote(SQLModel, table=True):
    base: str = Field(..., primary_key=True)
    quote: str = Field(..., primary_key=True)
    price: float
    volume_24h: float
    volume_change_24h: float
    percent_change_1h: float
    percent_change_24h: float
    percent_change_7d: float
    percent_change_30d: float
    percent_change_60d: float
    percent_change_90d: float
    market_cap: float
    market_cap_dominance: float
    fully_diluted_market_cap: float
    tvl: float | None
    last_updated: datetime.datetime = Field(..., primary_key=True)

    __table_args__ = {'schema': 'stats'}

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return "cmc"

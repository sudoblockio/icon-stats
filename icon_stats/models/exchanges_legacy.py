from pydantic import ConfigDict
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel
from datetime import datetime


class ExchangesLegacy(SQLModel):
    marketName: str = None
    tradeName: str = None
    createDate: datetime = None
    price: float = None
    prePrice: float = None
    dailyRate: float = None
    volume: float = None
    marketCap: float = None

    model_config = ConfigDict(
        extra='ignore',
    )

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return "exchanges_legacy"

from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel
from typing import Optional


class CmcListingsLatest(SQLModel):
    address: Optional[str] = Field(..., primary_key=True)
    # id:
    # name: Optional[str] = Field(..., primary_key=True)
    # symbol
    # slug
    # cmc_rank
    # num_market_pairs
    # circulating_supply
    # total_supply
    # max_supply
    # infinite_supply
    # last_updated
    # date_added
    # tags

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return ""

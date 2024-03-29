from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship

from icon_stats.db_base import BaseSQLModel

if TYPE_CHECKING:
    from icon_stats.models.contracts import Contract


class Token(BaseSQLModel, table=True):
    address: str = Field(
        sa_column=Column(
            "address",
            String(),
            ForeignKey("stats.contracts.address"),
            primary_key=True,
        ),
    )
    contract: Optional["Contract"] = Relationship(back_populates="token")

    name: Optional[str] = Field(None)
    symbol: Optional[str] = Field(None)
    decimals: Optional[str] = Field(None)
    is_nft: Optional[bool] = Field(None)
    contract_type: Optional[str] = Field(None)

    # Volume
    volume_24h: Optional[float] = Field(0)
    volume_7d: Optional[float] = Field(0)
    volume_30d: Optional[float] = Field(0)
    volume_24h_prev: Optional[float] = Field(0)
    volume_7d_prev: Optional[float] = Field(0)
    volume_30d_prev: Optional[float] = Field(0)

    # Token Transfers
    token_transfers_24h: Optional[int] = Field(None)
    token_transfers_7d: Optional[int] = Field(None)
    token_transfers_30d: Optional[int] = Field(None)
    token_transfers_24h_prev: Optional[int] = Field(None)
    token_transfers_7d_prev: Optional[int] = Field(None)
    token_transfers_30d_prev: Optional[int] = Field(None)
    # Fees burned
    fees_burned_24h: Optional[int] = Field(None)
    fees_burned_7d: Optional[int] = Field(None)
    fees_burned_30d: Optional[int] = Field(None)
    fees_burned_24h_prev: Optional[int] = Field(None)
    fees_burned_7d_prev: Optional[int] = Field(None)
    fees_burned_30d_prev: Optional[int] = Field(None)
    # Unique addresses
    unique_addresses_24h: Optional[int] = Field(None)
    unique_addresses_7d: Optional[int] = Field(None)
    unique_addresses_30d: Optional[int] = Field(None)
    unique_addresses_24h_prev: Optional[int] = Field(None)
    unique_addresses_7d_prev: Optional[int] = Field(None)
    unique_addresses_30d_prev: Optional[int] = Field(None)

    last_updated_timestamp: Optional[int] = Field(None)

    __table_args__ = {"schema": "stats"}

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return "tokens"

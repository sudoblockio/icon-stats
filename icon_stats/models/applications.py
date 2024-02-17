from typing import TYPE_CHECKING, Optional

from pydantic import condecimal
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship

from icon_stats.db_base import BaseSQLModel

if TYPE_CHECKING:
    from icon_stats.models.contracts import Contract


class Application(BaseSQLModel, table=True):
    id: str = Field(..., primary_key=True)

    contracts: list["Contract"] = Relationship(back_populates="application")

    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    url: Optional[str] = Field(None)
    logo: Optional[str] = Field(None)

    # Transactions
    transactions_24h: Optional[int] = Field(None)
    transactions_7d: Optional[int] = Field(None)
    transactions_30d: Optional[int] = Field(None)
    # Fees burned
    fees_burned_24h: Optional[int] = Field(None)
    fees_burned_7d: Optional[int] = Field(None)
    fees_burned_30d: Optional[int] = Field(None)
    # Transaction addresses
    transaction_addresses_24h: Optional[int] = Field(None)
    transaction_addresses_7d: Optional[int] = Field(None)
    transaction_addresses_30d: Optional[int] = Field(None)
    # Token Transfers
    token_transfers_24h: Optional[int] = Field(None)
    token_transfers_7d: Optional[int] = Field(None)
    token_transfers_30d: Optional[int] = Field(None)
    # Volume
    volume_24h: Optional[float] = Field(None)
    volume_7d: Optional[float] = Field(None)
    volume_30d: Optional[float] = Field(None)
    # Token transfer addresses
    token_transfer_addresses_24h: Optional[int] = Field(None)
    token_transfer_addresses_7d: Optional[int] = Field(None)
    token_transfer_addresses_30d: Optional[int] = Field(None)

    last_updated_timestamp: Optional[int] = Field(None)

    __table_args__ = {"schema": "stats"}

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return "applications"

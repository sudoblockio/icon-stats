from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship

from icon_stats.db_base import BaseSQLModel

if TYPE_CHECKING:
    from icon_stats.models.applications import Application
    from icon_stats.models.tokens import Token


class Contract(BaseSQLModel, table=True):
    address: str = Field(..., primary_key=True, unique=True)
    application_id: str = Field(
        sa_column=Column(
            "application_id",
            String(),
            ForeignKey("stats.applications.id"),
            primary_key=True,
        ),
    )
    application: Optional["Application"] = Relationship(back_populates="contracts")
    token: Optional["Token"] = Relationship(back_populates="contract")

    name: Optional[str] = Field(None)

    # Transactions
    transactions_24h: Optional[int] = Field(None)
    transactions_7d: Optional[int] = Field(None)
    transactions_30d: Optional[int] = Field(None)
    # Fees burned
    fees_burned_24h: Optional[int] = Field(None)
    fees_burned_7d: Optional[int] = Field(None)
    fees_burned_30d: Optional[int] = Field(None)
    # Unique addresses
    unique_addresses_24h: Optional[int] = Field(None)
    unique_addresses_7d: Optional[int] = Field(None)
    unique_addresses_30d: Optional[int] = Field(None)

    last_updated_timestamp: Optional[int] = Field(None)

    __table_args__ = {"schema": "stats"}

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return "contracts"

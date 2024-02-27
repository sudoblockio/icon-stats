from typing import Optional

from sqlalchemy.orm import declared_attr
from sqlmodel import Field

from icon_stats.db_base import BaseSQLModel


class Ecosystem(BaseSQLModel, table=True):
    id: int = Field(..., primary_key=True, unique=True)

    # Contracts
    ## Transactions
    transactions_24h: Optional[int] = Field(None)
    transactions_7d: Optional[int] = Field(None)
    transactions_30d: Optional[int] = Field(None)
    transactions_24h_prev: Optional[int] = Field(None)
    transactions_7d_prev: Optional[int] = Field(None)
    transactions_30d_prev: Optional[int] = Field(None)
    ## Fees burned
    fees_burned_24h: Optional[int] = Field(None)
    fees_burned_7d: Optional[int] = Field(None)
    fees_burned_30d: Optional[int] = Field(None)
    fees_burned_24h_prev: Optional[int] = Field(None)
    fees_burned_7d_prev: Optional[int] = Field(None)
    fees_burned_30d_prev: Optional[int] = Field(None)
    ## Transaction addresses
    transaction_addresses_24h: Optional[int] = Field(None)
    transaction_addresses_7d: Optional[int] = Field(None)
    transaction_addresses_30d: Optional[int] = Field(None)
    transaction_addresses_24h_prev: Optional[int] = Field(None)
    transaction_addresses_7d_prev: Optional[int] = Field(None)
    transaction_addresses_30d_prev: Optional[int] = Field(None)
    # Tokens
    ## Token Transfers
    token_transfers_24h: Optional[int] = Field(None)
    token_transfers_7d: Optional[int] = Field(None)
    token_transfers_30d: Optional[int] = Field(None)
    token_transfers_24h_prev: Optional[int] = Field(None)
    token_transfers_7d_prev: Optional[int] = Field(None)
    token_transfers_30d_prev: Optional[int] = Field(None)
    # Token transfer addresses
    token_transfer_addresses_24h: Optional[int] = Field(None)
    token_transfer_addresses_7d: Optional[int] = Field(None)
    token_transfer_addresses_30d: Optional[int] = Field(None)
    token_transfer_addresses_24h_prev: Optional[int] = Field(None)
    token_transfer_addresses_7d_prev: Optional[int] = Field(None)
    token_transfer_addresses_30d_prev: Optional[int] = Field(None)

    last_updated_timestamp: Optional[int] = Field(None)

    __table_args__ = {"schema": "stats"}

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return "ecosystem"

from pydantic import condecimal
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel
from typing import Optional

CondecimalType = condecimal(max_digits=28, decimal_places=0)


class TokenStats(SQLModel):
    address: Optional[str] = Field(..., primary_key=True)
    token_name: Optional[str] = Field(None)

    # Volume
    volume_24h: Optional[CondecimalType] = Field(None)
    volume_7d: Optional[CondecimalType] = Field(None)
    volume_30d: Optional[CondecimalType] = Field(None)

    # Transactions
    transactions_24h: Optional[int] = Field(None)
    transactions_7d: Optional[int] = Field(None)
    transactions_30d: Optional[int] = Field(None)

    # Token Transfers
    token_transfers_24h: Optional[int] = Field(None)
    token_transfers_7d: Optional[int] = Field(None)
    token_transfers_30d: Optional[int] = Field(None)

    last_updated_block: Optional[int] = Field(None)

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return "token_stats"

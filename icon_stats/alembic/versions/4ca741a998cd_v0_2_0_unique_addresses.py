"""v0.2.0-unique-addresses

Revision ID: 4ca741a998cd
Revises: c02c2fa1061d
Create Date: 2024-02-13 23:55:50.497192

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4ca741a998cd"
down_revision: Union[str, None] = "c02c2fa1061d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "applications",
        sa.Column("transaction_addresses_24h", sa.Integer(), nullable=True),
        schema="stats",
    )
    op.add_column(
        "applications",
        sa.Column("transaction_addresses_7d", sa.Integer(), nullable=True),
        schema="stats",
    )
    op.add_column(
        "applications",
        sa.Column("transaction_addresses_30d", sa.Integer(), nullable=True),
        schema="stats",
    )
    op.add_column(
        "applications",
        sa.Column("token_transfer_addresses_24h", sa.Integer(), nullable=True),
        schema="stats",
    )
    op.add_column(
        "applications",
        sa.Column("token_transfer_addresses_7d", sa.Integer(), nullable=True),
        schema="stats",
    )
    op.add_column(
        "applications",
        sa.Column("token_transfer_addresses_30d", sa.Integer(), nullable=True),
        schema="stats",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("applications", "token_transfer_addresses_30d", schema="stats")
    op.drop_column("applications", "token_transfer_addresses_7d", schema="stats")
    op.drop_column("applications", "token_transfer_addresses_24h", schema="stats")
    op.drop_column("applications", "transaction_addresses_30d", schema="stats")
    op.drop_column("applications", "transaction_addresses_7d", schema="stats")
    op.drop_column("applications", "transaction_addresses_24h", schema="stats")
    # ### end Alembic commands ###

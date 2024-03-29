"""v0.3.0-all-tokens

Revision ID: 3834262fdf64
Revises: 4ca741a998cd
Create Date: 2024-02-17 01:43:20.844130

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3834262fdf64"
down_revision: Union[str, None] = "4ca741a998cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "applications", "name", existing_type=sa.VARCHAR(), nullable=True, schema="stats"
    )
    op.alter_column(
        "applications", "description", existing_type=sa.VARCHAR(), nullable=True, schema="stats"
    )
    op.alter_column(
        "applications", "url", existing_type=sa.VARCHAR(), nullable=True, schema="stats"
    )
    op.alter_column(
        "applications", "logo", existing_type=sa.VARCHAR(), nullable=True, schema="stats"
    )
    op.add_column("tokens", sa.Column("is_nft", sa.Boolean(), nullable=True), schema="stats")
    op.add_column(
        "tokens",
        sa.Column("contract_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        schema="stats",
    )
    op.alter_column(
        "tokens",
        "decimals",
        existing_type=sa.INTEGER(),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=True,
        schema="stats",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "tokens",
        "decimals",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=sa.INTEGER(),
        existing_nullable=True,
        schema="stats",
    )
    op.drop_column("tokens", "contract_type", schema="stats")
    op.drop_column("tokens", "is_nft", schema="stats")
    op.alter_column(
        "applications", "logo", existing_type=sa.VARCHAR(), nullable=False, schema="stats"
    )
    op.alter_column(
        "applications", "url", existing_type=sa.VARCHAR(), nullable=False, schema="stats"
    )
    op.alter_column(
        "applications", "description", existing_type=sa.VARCHAR(), nullable=False, schema="stats"
    )
    op.alter_column(
        "applications", "name", existing_type=sa.VARCHAR(), nullable=False, schema="stats"
    )
    # ### end Alembic commands ###

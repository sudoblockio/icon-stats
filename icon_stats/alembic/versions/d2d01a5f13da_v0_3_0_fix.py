"""v0.3.0-fix

Revision ID: d2d01a5f13da
Revises: 5d35947228b7
Create Date: 2024-03-19 13:27:31.027184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = 'd2d01a5f13da'
down_revision: Union[str, None] = '5d35947228b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'ecosystem', ['id'], schema='stats')
    op.add_column('tokens', sa.Column('volume_24h_prev', sa.Float(), nullable=True), schema='stats')
    op.add_column('tokens', sa.Column('volume_7d_prev', sa.Float(), nullable=True), schema='stats')
    op.add_column('tokens', sa.Column('volume_30d_prev', sa.Float(), nullable=True), schema='stats')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tokens', 'volume_30d_prev', schema='stats')
    op.drop_column('tokens', 'volume_7d_prev', schema='stats')
    op.drop_column('tokens', 'volume_24h_prev', schema='stats')
    op.drop_constraint(None, 'ecosystem', schema='stats', type_='unique')
    # ### end Alembic commands ###

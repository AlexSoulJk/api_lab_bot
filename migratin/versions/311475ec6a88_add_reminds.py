"""add reminds

Revision ID: 311475ec6a88
Revises: 685be8fa4e99
Create Date: 2024-02-22 23:28:25.833340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '311475ec6a88'
down_revision: Union[str, None] = '685be8fa4e99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('remind',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=100), nullable=True),
    sa.Column('file_url', sa.String(length=100), nullable=True),
    sa.Column('image_url', sa.String(length=100), nullable=True),
    sa.Column('date_start', sa.Date(), nullable=False),
    sa.Column('date_deadline', sa.Date(), nullable=True),
    sa.Column('date_finish', sa.Date(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('remind')
    # ### end Alembic commands ###
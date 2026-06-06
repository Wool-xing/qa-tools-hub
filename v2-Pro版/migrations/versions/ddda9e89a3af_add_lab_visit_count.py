"""add_lab_visit_count

Revision ID: ddda9e89a3af
Revises: 732fc3ca015e
Create Date: 2026-06-06 14:10:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ddda9e89a3af'
down_revision: Union[str, Sequence[str], None] = '732fc3ca015e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('lab_visit_count', sa.Integer(), nullable=True, server_default='0'))

def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('lab_visit_count')

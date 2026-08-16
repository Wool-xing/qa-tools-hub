"""add_missing_tables

Revision ID: 732fc3ca015e
Revises: 792006b894b4
Create Date: 2026-05-19 02:53:24.845333

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '732fc3ca015e'
down_revision: Union[str, Sequence[str], None] = '792006b894b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add 6 missing tables + missing columns."""
    # Create 6 tables missing from initial migration
    op.create_table('achievements',
        sa.Column('key', sa.String(50), primary_key=True),
        sa.Column('icon', sa.String(10), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('desc', sa.String(200), nullable=False),
        sa.Column('condition_type', sa.String(30), nullable=False),
        sa.Column('condition_value', sa.String(50), nullable=False),
    )
    op.create_table('user_achievements',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('achievement_key', sa.String(50), nullable=False),
        sa.Column('earned_at', sa.DateTime),
    )
    op.create_table('teams',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('invite_code', sa.String(16), unique=True, nullable=False),
        sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime),
    )
    op.create_table('team_members',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('team_id', sa.Integer, sa.ForeignKey('teams.id'), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role', sa.String(20), default='member'),
        sa.Column('joined_at', sa.DateTime),
    )
    op.create_table('test_cases',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), index=True),
        sa.Column('title', sa.String(300)),
        sa.Column('steps', sa.Text),
        sa.Column('expected_result', sa.Text),
        sa.Column('priority', sa.String(10), default='P2'),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('tags', sa.String(500), nullable=True),
        sa.Column('folder', sa.String(100), default='默认'),
        sa.Column('team_id', sa.Integer, sa.ForeignKey('teams.id'), nullable=True, index=True),
        sa.Column('level_id', sa.Integer, sa.ForeignKey('levels.id'), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )
    op.create_table('test_runs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('test_case_id', sa.Integer, sa.ForeignKey('test_cases.id', ondelete='CASCADE'), index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), index=True),
        sa.Column('status', sa.String(10), default='passed'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime),
    )
    op.add_column('users', sa.Column('last_active_date', sa.String(length=10), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'last_active_date')
    op.drop_table('test_runs')
    op.drop_table('test_cases')
    op.drop_table('team_members')
    op.drop_table('teams')
    op.drop_table('user_achievements')
    op.drop_table('achievements')

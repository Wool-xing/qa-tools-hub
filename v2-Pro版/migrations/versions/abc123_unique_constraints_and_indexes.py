"""Add missing unique constraints and performance indexes.

Revision ID: abc123uqc
Revises: ddda9e89a3af
Create Date: 2026-06-06
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'abc123uqc'
down_revision = 'ddda9e89a3af'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Deduplicate user_level_progress — keep row with highest score, then most attempts
    op.execute("""
        DELETE FROM user_level_progress WHERE id NOT IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (
                    PARTITION BY user_id, level_id ORDER BY score DESC, attempts DESC
                ) AS rn
                FROM user_level_progress
            ) WHERE rn = 1
        )
    """)
    # 2. Add unique constraint on user_level_progress
    with op.batch_alter_table('user_level_progress') as batch:
        batch.create_unique_constraint('uq_user_level', ['user_id', 'level_id'])

    # 3. Deduplicate team_members
    op.execute("""
        DELETE FROM team_members WHERE id NOT IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (
                    PARTITION BY team_id, user_id ORDER BY id
                ) AS rn
                FROM team_members
            ) WHERE rn = 1
        )
    """)
    # 4. Add unique constraint on team_members
    with op.batch_alter_table('team_members') as batch:
        batch.create_unique_constraint('uq_team_member', ['team_id', 'user_id'])

    # 5. Add performance indexes
    with op.batch_alter_table('user_achievements') as batch:
        batch.create_index('ix_user_achievements_user_id', ['user_id'])
        batch.create_unique_constraint('uq_user_achievement', ['user_id', 'achievement_key'])

    with op.batch_alter_table('user_level_progress') as batch:
        batch.create_index('ix_ulp_level_id', ['level_id'])
        batch.create_index('ix_ulp_status', ['status'])

    with op.batch_alter_table('test_cases') as batch:
        batch.create_index('ix_test_cases_folder', ['folder'])
        batch.create_index('ix_test_cases_updated_at', ['updated_at'])


def downgrade():
    with op.batch_alter_table('test_cases') as batch:
        batch.drop_index('ix_test_cases_updated_at')
        batch.drop_index('ix_test_cases_folder')

    with op.batch_alter_table('user_level_progress') as batch:
        batch.drop_index('ix_ulp_status')
        batch.drop_index('ix_ulp_level_id')

    with op.batch_alter_table('user_achievements') as batch:
        batch.drop_constraint('uq_user_achievement')
        batch.drop_index('ix_user_achievements_user_id')

    with op.batch_alter_table('team_members') as batch:
        batch.drop_constraint('uq_team_member')

    with op.batch_alter_table('user_level_progress') as batch:
        batch.drop_constraint('uq_user_level')

"""baseline

Revision ID: 0001_baseline
Revises: 
Create Date: 2025-08-13

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0001_baseline'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Baseline only; schema established via /db migrations.
    pass


def downgrade() -> None:
    pass


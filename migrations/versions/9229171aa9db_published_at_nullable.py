"""'published_at_nullable'

Revision ID: 9229171aa9db
Revises: 2a9aecc5c88c
Create Date: 2026-04-13 11:46:53.133704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9229171aa9db'
down_revision: Union[str, None] = '2a9aecc5c88c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('jobs', 'published_at', nullable=True)
    op.create_index('uq_jobs_url_null_published_at', 'jobs', ['url'], unique=True,
                    postgresql_where=sa.text('published_at IS NULL'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_jobs_url_null_published_at', table_name='jobs')
    op.alter_column('jobs', 'published_at', nullable=False)

"""rename works to jobs, update sites, add scraping_sessions and raw_responses

Revision ID: 9f3d2e1a0b4c
Revises: 5aae5fcd300e
Create Date: 2026-03-10

"""
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = '9f3d2e1a0b4c'
down_revision = '5aae5fcd300e'
branch_labels = None
depends_on = None

SITES_SEED = [
    {'name': 'DOU',      'url': 'https://jobs.dou.ua/vacancies/?category=Python&exp=1-3'},
    {'name': 'Djinni',   'url': 'https://djinni.co/jobs/?primary_keyword=Python'},
    {'name': 'RobotaUA', 'url': 'https://robota.ua'},
    {'name': 'WorkUA',   'url': 'https://www.work.ua/jobs-remote-it-industry-it-python/'},
]


def _table_exists(conn, name):
    return inspect(conn).has_table(name)


def _column_exists(conn, table, column):
    cols = [c['name'] for c in inspect(conn).get_columns(table)]
    return column in cols


def _constraint_exists(conn, table, constraint):
    names = [c['name'] for c in inspect(conn).get_unique_constraints(table)]
    return constraint in names


def upgrade():
    conn = op.get_bind()

    # --- works → jobs (migrate data if works exists) ---
    if _table_exists(conn, 'works'):
        if _table_exists(conn, 'jobs'):
            # jobs already created by create_all(); copy data from works then drop works
            conn.execute(sa.text(
                'INSERT INTO jobs (id, url, title, description, salary, city, company, published_at, created_at, updated_at) '
                'SELECT id, url, title, description, salary, city, company, published_at, created_at, updated_at FROM works '
                'ON CONFLICT (url) DO NOTHING'
            ))
            op.drop_table('works')
        else:
            op.rename_table('works', 'jobs')

    # --- sites: add proxy column if missing ---
    if not _column_exists(conn, 'sites', 'proxy'):
        op.add_column('sites', sa.Column('proxy', sa.Text(), nullable=True))

    # --- sites: add enabled column if missing ---
    if not _column_exists(conn, 'sites', 'enabled'):
        op.add_column('sites', sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'))

    # --- sites: unique constraint on name if missing ---
    if not _constraint_exists(conn, 'sites', 'uq_sites_name'):
        op.create_unique_constraint('uq_sites_name', 'sites', ['name'])

    # --- scraping_sessions ---
    if not _table_exists(conn, 'scraping_sessions'):
        op.create_table(
            'scraping_sessions',
            sa.Column('id', sa.BigInteger(), primary_key=True),
            sa.Column('site_id', sa.BigInteger(), sa.ForeignKey('sites.id'), nullable=False),
            sa.Column('status', sa.String(), nullable=False),
            sa.Column('jobs_found', sa.Integer(), nullable=True),
            sa.Column('error', sa.Text(), nullable=True),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        )

    # --- raw_responses ---
    if not _table_exists(conn, 'raw_responses'):
        op.create_table(
            'raw_responses',
            sa.Column('id', sa.BigInteger(), primary_key=True),
            sa.Column('session_id', sa.BigInteger(), sa.ForeignKey('scraping_sessions.id'), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        )

    # --- seed sites (only if table is empty) ---
    count = conn.execute(sa.text('SELECT COUNT(*) FROM sites')).scalar()
    if count == 0:
        now = datetime.now(timezone.utc)
        sites_table = sa.table(
            'sites',
            sa.column('name', sa.String),
            sa.column('url', sa.Text),
            sa.column('proxy', sa.Text),
            sa.column('enabled', sa.Boolean),
            sa.column('created_at', sa.DateTime(timezone=True)),
            sa.column('updated_at', sa.DateTime(timezone=True)),
        )
        op.bulk_insert(sites_table, [
            {**site, 'proxy': None, 'enabled': True, 'created_at': now, 'updated_at': now}
            for site in SITES_SEED
        ])


def downgrade():
    op.drop_table('raw_responses')
    op.drop_table('scraping_sessions')
    op.drop_constraint('uq_sites_name', 'sites', type_='unique')
    op.drop_column('sites', 'enabled')
    op.drop_column('sites', 'proxy')
    op.rename_table('jobs', 'works')

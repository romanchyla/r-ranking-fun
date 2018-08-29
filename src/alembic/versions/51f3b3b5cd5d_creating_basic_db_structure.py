"""Creating basic DB structure

Revision ID: 51f3b3b5cd5d
Revises: None
Create Date: 2015-13-09 20:13:58.241566

"""
# revision identifiers, used by Alembic.
revision = '51f3b3b5cd5d'
down_revision = None

from alembic import op
import sqlalchemy as sa
import datetime

from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Index, TIMESTAMP
import datetime


def upgrade():
    op.create_table('experiments',
        sa.Column('eid', sa.Integer, primary_key=True),
        sa.Column('query', sa.String(length=1024)),
        sa.Column('experiment_params', sa.Text),
        sa.Column('query_results', sa.Text),
        sa.Column('relevant', sa.Text),
        sa.Column('created', TIMESTAMP, default=datetime.datetime.utcnow),
        sa.Column('updated', TIMESTAMP),
        sa.Column('started', TIMESTAMP),
        sa.Column('finished', TIMESTAMP),
        sa.Column('reporter', sa.String(length=1024), nullable=True),
        sa.Column('progress', Integer),
        sa.Index('ix_eid', 'eid')
    )

def downgrade():
    op.drop_table('experiments')
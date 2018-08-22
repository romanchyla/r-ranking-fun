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
from sqlalchemy import String, Integer, Index


def upgrade():
    op.create_table('experiments',
        sa.Column('eid', sa.Integer, primary_key=True),
        sa.Column('query', sa.String(length=1024), nullable=False),
        sa.Column('query_params', sa.String(length=1024), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('experiment_params', sa.String(length=1024), nullable=False),
        Index('ix_eid', 'eid')
    )    

def downgrade():
    op.drop_table('experiments')
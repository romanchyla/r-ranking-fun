"""Adding results

Revision ID: 3b47cb6a817
Revises: 51f3b3b5cd5d
Create Date: 2018-09-04 17:25:03.158848

"""

# revision identifiers, used by Alembic.
revision = '3b47cb6a817'
down_revision = '51f3b3b5cd5d'

from alembic import op
import sqlalchemy as sa

                               


def upgrade():
    op.add_column('experiments', sa.Column('experiment_results', sa.Text))   


def downgrade():
    op.drop_column('experiments', 'experiment_results')

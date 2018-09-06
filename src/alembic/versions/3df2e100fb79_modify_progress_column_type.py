"""Modify progress column type

Revision ID: 3df2e100fb79
Revises: 3b47cb6a817
Create Date: 2018-09-05 23:13:58.552703

"""

# revision identifiers, used by Alembic.
revision = '3df2e100fb79'
down_revision = '3b47cb6a817'

from alembic import op
import sqlalchemy as sa

                               


def upgrade():
    with op.batch_alter_table('experiments') as batch_op:
        batch_op.drop_column('progress')
        batch_op.add_column(sa.Column('progress', sa.FLOAT))

def downgrade():
    with op.batch_alter_table('experiments') as batch_op:
        batch_op.drop_column('progress')
        batch_op.add_column(sa.Column('progress', sa.Integer))

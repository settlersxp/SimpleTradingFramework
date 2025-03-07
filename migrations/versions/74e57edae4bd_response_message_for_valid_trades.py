"""response message for valid trades

Revision ID: 74e57edae4bd
Revises: 6fdd2076b3ba
Create Date: 2025-02-23 09:33:49.524844

"""
from alembic import op
import sqlalchemy as sa
from alembic import context

# revision identifiers, used by Alembic.
revision = '74e57edae4bd'
down_revision = '6fdd2076b3ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prop_firm_trades', schema=None) as batch_op:
        batch_op.add_column(sa.Column('response', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prop_firm_trades', schema=None) as batch_op:
        if context.has_column('prop_firm_trades', 'response'):
            batch_op.drop_column('response')

    # ### end Alembic commands ###

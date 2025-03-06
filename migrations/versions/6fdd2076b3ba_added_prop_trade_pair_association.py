"""added prop trade pair association

Revision ID: 6fdd2076b3ba
Revises: a4e3375671be
Create Date: 2025-02-18 21:12:34.847007

"""
from alembic import context, op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6fdd2076b3ba'
down_revision = 'a4e3375671be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    if not context.has_table('prop_firm_trade_pair_association'):
        op.create_table('prop_firm_trade_pair_association',
                        sa.Column('prop_firm_id', sa.Integer(),
                                  nullable=False),
                        sa.Column('label', sa.String(
                            length=100), nullable=False),
                        sa.Column('trade_pair_id',
                                  sa.Integer(), nullable=False),
                        sa.Column('platform_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['prop_firm_id'], ['prop_firms.id'], ),
                        sa.ForeignKeyConstraint(
                            ['trade_pair_id'], ['trade_pairs.id'], ),
                        sa.PrimaryKeyConstraint(
                            'prop_firm_id', 'trade_pair_id')
                        )
    else:
        op.create_table('prop_firm_trade_pair_association',
                        sa.Column('prop_firm_id', sa.Integer(),
                                  nullable=False),
                        sa.Column('label', sa.String(
                            length=100), nullable=False),
                        sa.Column('trade_pair_id',
                                  sa.Integer(), nullable=False),
                        sa.Column('platform_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['prop_firm_id'], ['prop_firms.id'], ),
                        sa.ForeignKeyConstraint(
                            ['trade_pair_id'], ['trade_pairs.id'], ),
                        sa.PrimaryKeyConstraint(
                            'prop_firm_id', 'trade_pair_id')
                        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    if context.has_table('prop_firm_trade_pair_association'):
        op.drop_table('prop_firm_trade_pair_association')
    # ### end Alembic commands ###

"""Add new columns to PropFirm

Revision ID: 111af910ca38
Revises: Added new columns to the PropFirm model to easily configure them.
Create Date: 2025-01-22 19:14:59.695984

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '111af910ca38'
down_revision = None
branch_labels = None
depends_on = None


def has_column(table_name, column_name):
    """Check if a column exists in a table"""
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prop_firms', schema=None) as batch_op:
        # Add columns only if they don't exist
        if not has_column('prop_firms', 'is_active'):
            batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))
        if not has_column('prop_firms', 'username'):
            batch_op.add_column(sa.Column('username', sa.String(length=100), nullable=False, server_default='default_user'))
        if not has_column('prop_firms', 'password'):
            batch_op.add_column(sa.Column('password', sa.String(length=100), nullable=False, server_default='default_pass'))
        if not has_column('prop_firms', 'ip_address'):
            batch_op.add_column(sa.Column('ip_address', sa.String(length=100), nullable=False, server_default='127.0.0.1'))
        if not has_column('prop_firms', 'port'):
            batch_op.add_column(sa.Column('port', sa.Integer(), nullable=False, server_default='8080'))
        if not has_column('prop_firms', 'platform_type'):
            batch_op.add_column(sa.Column('platform_type', sa.String(length=100), nullable=False, server_default='MT4'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prop_firms', schema=None) as batch_op:
        # Drop columns only if they exist
        if has_column('prop_firms', 'platform_type'):
            batch_op.drop_column('platform_type')
        if has_column('prop_firms', 'port'):
            batch_op.drop_column('port')
        if has_column('prop_firms', 'ip_address'):
            batch_op.drop_column('ip_address')
        if has_column('prop_firms', 'password'):
            batch_op.drop_column('password')
        if has_column('prop_firms', 'username'):
            batch_op.drop_column('username')
        if has_column('prop_firms', 'is_active'):
            batch_op.drop_column('is_active')

    # ### end Alembic commands ###

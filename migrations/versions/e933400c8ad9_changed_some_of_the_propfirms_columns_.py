"""Changed some of the PropFirms columns to optional

Revision ID: e933400c8ad9
Revises: 111af910ca38
Create Date: 2025-01-22 20:16:55.928950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e933400c8ad9'
down_revision = '111af910ca38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prop_firms', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=100),
               nullable=True,
               existing_server_default=sa.text("'default_user'"))
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=100),
               nullable=True,
               existing_server_default=sa.text("'default_pass'"))
        batch_op.alter_column('ip_address',
               existing_type=sa.VARCHAR(length=100),
               nullable=True,
               existing_server_default=sa.text("'127.0.0.1'"))
        batch_op.alter_column('port',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text("'8080'"))
        batch_op.alter_column('platform_type',
               existing_type=sa.VARCHAR(length=100),
               nullable=True,
               existing_server_default=sa.text("'MT4'"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prop_firms', schema=None) as batch_op:
        batch_op.alter_column('platform_type',
               existing_type=sa.VARCHAR(length=100),
               nullable=False,
               existing_server_default=sa.text("'MT4'"))
        batch_op.alter_column('port',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text("'8080'"))
        batch_op.alter_column('ip_address',
               existing_type=sa.VARCHAR(length=100),
               nullable=False,
               existing_server_default=sa.text("'127.0.0.1'"))
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=100),
               nullable=False,
               existing_server_default=sa.text("'default_pass'"))
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=100),
               nullable=False,
               existing_server_default=sa.text("'default_user'"))

    # ### end Alembic commands ###

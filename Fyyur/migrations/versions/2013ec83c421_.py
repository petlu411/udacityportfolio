"""empty message

Revision ID: 2013ec83c421
Revises: 1b0291827edb
Create Date: 2020-06-09 11:19:04.602248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2013ec83c421'
down_revision = '1b0291827edb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Show', 'start_time',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Show', 'start_time',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###

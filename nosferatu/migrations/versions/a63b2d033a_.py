"""empty message

Revision ID: a63b2d033a
Revises: None
Create Date: 2015-08-22 14:18:38.605518

"""

# revision identifiers, used by Alembic.
revision = 'a63b2d033a'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nodes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('ip_addr', postgresql.INET(), nullable=True),
    sa.Column('mac_addr', postgresql.MACADDR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('nodes')
    ### end Alembic commands ###

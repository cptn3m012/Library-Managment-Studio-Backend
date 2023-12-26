"""replacement of the description field with the year of publication and the publishing house in the book model

Revision ID: 437d20caee4d
Revises: 6080132c4f87
Create Date: 2023-12-16 14:50:36.760871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '437d20caee4d'
down_revision = '6080132c4f87'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rok_wydania', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('wydawnictwo', sa.String(length=255), nullable=True))
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.drop_column('wydawnictwo')
        batch_op.drop_column('rok_wydania')

    # ### end Alembic commands ###

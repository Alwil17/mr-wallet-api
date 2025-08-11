"""
Add category_id to transactions for user-defined categories
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('transactions', sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True))


def downgrade():
    op.drop_column('transactions', 'category_id')

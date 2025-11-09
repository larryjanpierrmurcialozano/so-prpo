from alembic import op
import sqlalchemy as sa

revision = '452dee38738f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=False),
    sa.Column('slug', sa.String(length=150), nullable=False),
    sa.Column('color_bg', sa.String(length=7), nullable=True),
    sa.Column('logo_url', sa.String(length=500), nullable=True),
    sa.Column('logo_size', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('image_url', sa.String(length=500), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('products')
    op.drop_table('pages')

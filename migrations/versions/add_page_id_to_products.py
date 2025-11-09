from alembic import op
import sqlalchemy as sa


revision = 'add_page_id_to_products'
down_revision = 'multiple_pages_support'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('products', sa.Column('page_id', sa.Integer(), nullable=True))
    
    op.create_foreign_key('fk_products_page_id', 'products', 'pages', ['page_id'], ['id'])
    
    op.execute("""
        UPDATE products 
        SET page_id = (
            SELECT pages.id 
            FROM pages 
            WHERE pages.owner_id = products.owner_id 
            LIMIT 1
        )
        WHERE page_id IS NULL
    """)
    
    op.alter_column('products', 'page_id', nullable=False)


def downgrade():
    op.drop_constraint('fk_products_page_id', 'products', type_='foreignkey')
    op.drop_column('products', 'page_id')

from alembic import op
import sqlalchemy as sa


revision = 'c3f4d5e6f789'
down_revision = 'add_last_login_cleanup'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('product_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    categories_table = sa.table('categories',
        sa.column('name', sa.String),
        sa.column('description', sa.Text),
        sa.column('is_default', sa.Boolean),
        sa.column('owner_id', sa.Integer)
    )
    
    op.bulk_insert(categories_table, [
        {'name': 'Electrónicos', 'description': 'Dispositivos electrónicos y tecnología', 'is_default': True, 'owner_id': None},
        {'name': 'Ropa y Accesorios', 'description': 'Prendas de vestir y complementos', 'is_default': True, 'owner_id': None},
        {'name': 'Hogar y Jardín', 'description': 'Artículos para el hogar y jardinería', 'is_default': True, 'owner_id': None},
        {'name': 'Deportes y Recreación', 'description': 'Equipos deportivos y entretenimiento', 'is_default': True, 'owner_id': None},
        {'name': 'Salud y Belleza', 'description': 'Productos de cuidado personal y salud', 'is_default': True, 'owner_id': None},
        {'name': 'Automóviles', 'description': 'Vehículos y accesorios automotrices', 'is_default': True, 'owner_id': None},
        {'name': 'Libros y Medios', 'description': 'Libros, música, películas y medios', 'is_default': True, 'owner_id': None},
        {'name': 'Comida y Bebidas', 'description': 'Alimentos, bebidas y productos gastronómicos', 'is_default': True, 'owner_id': None},
        {'name': 'Juguetes y Juegos', 'description': 'Juguetes, juegos y entretenimiento infantil', 'is_default': True, 'owner_id': None},
        {'name': 'Arte y Manualidades', 'description': 'Suministros artísticos y manualidades', 'is_default': True, 'owner_id': None}
    ])


def downgrade():
    op.drop_table('product_categories')
    op.drop_table('categories')

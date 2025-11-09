from alembic import op
import sqlalchemy as sa


revision = 'multiple_pages_support'
down_revision = 'add_last_login_cleanup'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

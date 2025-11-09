from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone


revision = 'add_last_login_cleanup'
down_revision = '60e58207aeee'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    # Remove last_login field from users table
    op.drop_column('users', 'last_login')

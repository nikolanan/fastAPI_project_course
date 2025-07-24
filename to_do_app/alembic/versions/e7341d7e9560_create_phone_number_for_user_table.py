"""Create phone number for user table

Revision ID: e7341d7e9560
Revises: 
Create Date: 2025-07-24 12:07:51.430302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7341d7e9560'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("phone_number",sa.String(),nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    print(" Running downgrade: dropping phone_number column")
    op.drop_column("users","phone_number")

"""message

Revision ID: af08adc91c01
Revises: 83a65c791906
Create Date: 2026-10-20 14:34:30.669719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af08adc91c01'
down_revision: Union[str, Sequence[str], None] = '83a65c791906'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

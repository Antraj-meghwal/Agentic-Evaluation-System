"""add upload rubric_path

Revision ID: a1b2c3d4e5f6
Revises: 0f50abfc61fd
Create Date: 2026-05-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f950501d991d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "uploaded_files",
        sa.Column("rubric_path", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("uploaded_files", "rubric_path")

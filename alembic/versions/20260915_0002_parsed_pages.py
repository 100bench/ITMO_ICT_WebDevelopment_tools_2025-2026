"""Добавляет результаты парсинга страниц для лабораторной работы 2."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260915_0002"
down_revision: Union[str, None] = "20260528_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "parsed_pages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("approach", sa.String(length=32), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_parsed_pages_owner_id"), "parsed_pages", ["owner_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_parsed_pages_owner_id"), table_name="parsed_pages")
    op.drop_table("parsed_pages")

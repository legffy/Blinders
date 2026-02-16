"""guardrail_state table + per-user domain uniqueness

Revision ID: <NEW_REVISION_ID>
Revises: a1986aa782c2
Create Date: 2026-02-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "33a5e8edf220"
down_revision: Union[str, Sequence[str], None] = "a1986aa782c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Drop the global UNIQUE index on domain
    op.drop_index("ix_domain_guardrails_domain", table_name="domain_guardrails")

    # 2) Recreate domain index as NON-unique (still useful for lookups)
    op.create_index(
        "ix_domain_guardrails_domain",
        "domain_guardrails",
        ["domain"],
        unique=False,
    )

    # 3) Add unique constraint per user + domain
    op.create_unique_constraint(
        "uq_user_domain",
        "domain_guardrails",
        ["user_id", "domain"],
    )

    # 4) Create guardrail_state table
    op.create_table(
        "guardrail_state",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    # Drop guardrail_state
    op.drop_table("guardrail_state")

    # Remove per-user uniqueness
    op.drop_constraint("uq_user_domain", "domain_guardrails", type_="unique")

    # Drop non-unique domain index
    op.drop_index("ix_domain_guardrails_domain", table_name="domain_guardrails")

    # Recreate UNIQUE domain index (original behavior)
    op.create_index(
        "ix_domain_guardrails_domain",
        "domain_guardrails",
        ["domain"],
        unique=True,
    )
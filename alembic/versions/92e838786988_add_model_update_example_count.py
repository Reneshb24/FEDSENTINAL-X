"""add model update example count

Revision ID: 92e838786988
Revises: add_incident_security_metadata
"""

from alembic import op
import sqlalchemy as sa


revision = "92e838786988"
down_revision = "add_incident_security_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "model_updates",
        sa.Column(
            "num_examples",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE model_updates "
        "SET num_examples = 0 "
        "WHERE num_examples IS NULL"
    )

    with op.batch_alter_table("model_updates") as batch_op:
        batch_op.alter_column(
            "num_examples",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("model_updates") as batch_op:
        batch_op.drop_column("num_examples")

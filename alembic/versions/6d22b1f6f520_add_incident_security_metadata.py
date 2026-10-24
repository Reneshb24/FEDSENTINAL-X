"""add incident security metadata

Revision ID: add_incident_security_metadata
Revises: 371bab5114b4
"""

from alembic import op
import sqlalchemy as sa


revision = "add_incident_security_metadata"
down_revision = "371bab5114b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "incidents",
        sa.Column(
            "incident_code",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "recommended_action",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "risk_score",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "confidence",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "evidence_json",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "assigned_to",
            sa.String(length=128),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "resolution_notes",
            sa.Text(),
            nullable=True,
        ),
    )

    # Existing rows need safe defaults.
    op.execute(
        "UPDATE incidents "
        "SET incident_code = id "
        "WHERE incident_code IS NULL"
    )

    op.execute(
        "UPDATE incidents "
        "SET recommended_action = 'REVIEW' "
        "WHERE recommended_action IS NULL"
    )

    op.execute(
        "UPDATE incidents "
        "SET risk_score = 0.0 "
        "WHERE risk_score IS NULL"
    )

    op.execute(
        "UPDATE incidents "
        "SET confidence = 0.0 "
        "WHERE confidence IS NULL"
    )

    op.execute(
        "UPDATE incidents "
        "SET evidence_json = '{}' "
        "WHERE evidence_json IS NULL"
    )

    with op.batch_alter_table("incidents") as batch_op:
        batch_op.alter_column(
            "incident_code",
            existing_type=sa.String(length=100),
            nullable=False,
        )
        batch_op.alter_column(
            "recommended_action",
            existing_type=sa.String(length=50),
            nullable=False,
        )
        batch_op.alter_column(
            "risk_score",
            existing_type=sa.Float(),
            nullable=False,
        )
        batch_op.alter_column(
            "confidence",
            existing_type=sa.Float(),
            nullable=False,
        )
        batch_op.alter_column(
            "evidence_json",
            existing_type=sa.Text(),
            nullable=False,
        )
        batch_op.create_unique_constraint(
            "uq_incidents_incident_code",
            ["incident_code"],
        )


def downgrade() -> None:
    with op.batch_alter_table("incidents") as batch_op:
        batch_op.drop_constraint(
            "uq_incidents_incident_code",
            type_="unique",
        )
        batch_op.drop_column("resolution_notes")
        batch_op.drop_column("assigned_to")
        batch_op.drop_column("evidence_json")
        batch_op.drop_column("confidence")
        batch_op.drop_column("risk_score")
        batch_op.drop_column("recommended_action")
        batch_op.drop_column("incident_code")
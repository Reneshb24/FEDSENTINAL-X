"""Add source_type column to dataset_versions table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "add_source_type_to_dataset_version"
down_revision = "371bab5114b4_add_round_configuration"  # adjust if needed
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "dataset_versions",
        sa.Column(
            "source_type",
            sa.String(length=30),
            nullable=False,
            server_default="LOCAL_UPLOAD",
        ),
    )
    # Remove server default after adding column (optional)
    op.alter_column("dataset_versions", "source_type", server_default=None)


def downgrade() -> None:
    op.drop_column("dataset_versions", "source_type")

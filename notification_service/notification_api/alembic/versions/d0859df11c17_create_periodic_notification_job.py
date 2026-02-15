"""create notifications and notification_targets tables

Revision ID: 20260214_create_notifications
Revises: None
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# ---------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------
revision = "20260214_create_notifications"
down_revision = None
branch_labels = None
depends_on = None


# ---------------------------------------------------------
# Upgrade
# ---------------------------------------------------------
def upgrade() -> None:
    # Ensure extension for UUID if needed
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # -----------------------------------------------------
    # notifications table
    # -----------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("event_key", sa.String(), nullable=False),
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("payload", postgresql.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="queued",
        ),
        sa.Column("idempotency_key", sa.String(), nullable=True),
        sa.Column(
            "created_by",
            sa.String(),
            nullable=True,
            server_default="system",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "scheduled_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "is_periodic",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "cron_expression",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "repeat_until",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # -----------------------------------------------------
    # Indexes for notifications
    # -----------------------------------------------------
    op.create_index(
        "ix_notifications_event_key",
        "notifications",
        ["event_key"],
    )

    op.create_index(
        "ix_notifications_status",
        "notifications",
        ["status"],
    )

    op.create_index(
        "ix_notifications_scheduled_at",
        "notifications",
        ["scheduled_at"],
    )

    op.create_index(
        "ix_notifications_is_periodic",
        "notifications",
        ["is_periodic"],
    )

    # Optional but recommended
    op.create_index(
        "ux_notifications_idempotency_key",
        "notifications",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    # -----------------------------------------------------
    # notification_targets table
    # -----------------------------------------------------
    op.create_table(
        "notification_targets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "notification_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "notifications.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "target_type",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "target_value",
            sa.String(),
            nullable=False,
        ),
    )

    # -----------------------------------------------------
    # Indexes for notification_targets
    # -----------------------------------------------------
    op.create_index(
        "ix_notification_targets_notification_id",
        "notification_targets",
        ["notification_id"],
    )

    op.create_index(
        "ix_notification_targets_target_value",
        "notification_targets",
        ["target_value"],
    )


# ---------------------------------------------------------
# Downgrade
# ---------------------------------------------------------
def downgrade() -> None:
    op.drop_index(
        "ix_notification_targets_target_value",
        table_name="notification_targets",
    )
    op.drop_index(
        "ix_notification_targets_notification_id",
        table_name="notification_targets",
    )
    op.drop_table("notification_targets")

    op.drop_index(
        "ux_notifications_idempotency_key",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_is_periodic",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_scheduled_at",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_status",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_event_key",
        table_name="notifications",
    )
    op.drop_table("notifications")

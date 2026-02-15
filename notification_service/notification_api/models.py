import uuid
from sqlalchemy import (
    Column,
    String,
    JSON,
    JSONB,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_key = Column(String, nullable=False)
    template_id = Column(UUID(as_uuid=True), nullable=True)

    payload = Column(JSONB, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="queued",
    )

    idempotency_key = Column(String, nullable=True)

    created_by = Column(String, default="system")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    scheduled_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    is_periodic = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    cron_expression = Column(
        String,
        nullable=True,
    )

    repeat_until = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    targets = relationship(
        "NotificationTarget",
        back_populates="notification",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def add_user_target(self, user_id: str) -> None:
        """
        Adds a single user target to the notification.
        Does NOT commit automatically.
        """

        target = NotificationTarget(
            notification_id=self.id,
            target_type="user",
            target_value=str(user_id),
        )

        self.targets.append(target)


class NotificationTarget(Base):
    __tablename__ = "notification_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id", ondelete="CASCADE"),
    )
    target_type = Column(String, nullable=False)  # user | segment
    target_value = Column(String, nullable=False)

    notification = relationship("Notification", back_populates="targets")

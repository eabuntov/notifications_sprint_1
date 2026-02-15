import uuid
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True)
    event_key = Column(String, nullable=False)
    payload = Column(String)
    template_id = Column(UUID(as_uuid=True))


class NotificationTarget(Base):
    __tablename__ = "notification_targets"

    id = Column(UUID(as_uuid=True), primary_key=True)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id"))
    target_type = Column(String)  # user | segment
    target_value = Column(String)


class NotificationSendLog(Base):
    __tablename__ = "notification_send_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True))
    channel = Column(String)
    status = Column(String)
    error = Column(String, nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "notification_id",
            "user_id",
            "channel",
            name="uniq_notification_user_channel",
        ),
    )


class UserNotificationSettings(Base):
    __tablename__ = "user_notification_settings"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    channel = Column(String, primary_key=True)
    enabled = Column(Boolean, nullable=False, default=True)
    frequency = Column(String, nullable=False, default="immediate")


class AuthUser(Base):
    __tablename__ = "auth_user"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    email = Column(String)
    is_active = Column(Boolean)

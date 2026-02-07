from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Notification, NotificationTarget
from .kafka import publish_notification


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_instant_notification(
        self,
        event_key: str,
        user_id: str,
        payload: dict,
        idempotency_key: str | None,
    ) -> Notification:
        notification = Notification(
            event_key=event_key,
            payload=payload,
            idempotency_key=idempotency_key,
        )

        target = NotificationTarget(
            target_type="user",
            target_value=str(user_id),
            notification=notification,
        )

        self.db.add(notification)
        self.db.add(target)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return (
                self.db.query(Notification)
                .filter(
                    Notification.event_key == event_key,
                    Notification.idempotency_key == idempotency_key,
                )
                .one()
            )

        publish_notification(str(notification.id))
        return notification

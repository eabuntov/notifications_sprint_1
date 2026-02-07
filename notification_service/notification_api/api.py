from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .db import SessionLocal
from .schemas import InstantNotificationRequest, NotificationResponse
from .services import NotificationService

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/v1/notifications/instant",
    response_model=NotificationResponse,
)
def create_instant_notification(
    request: InstantNotificationRequest,
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    notification = service.create_instant_notification(
        event_key=request.event_key,
        user_id=request.user_id,
        payload=request.payload,
        idempotency_key=request.idempotency_key,
    )

    return NotificationResponse(
        notification_id=notification.id,
        status=notification.status,
    )

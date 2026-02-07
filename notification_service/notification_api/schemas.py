from pydantic import BaseModel, Field
from typing import Dict, Optional
from uuid import UUID


class InstantNotificationRequest(BaseModel):
    event_key: str
    user_id: UUID
    payload: Dict
    idempotency_key: Optional[str] = Field(default=None)


class NotificationResponse(BaseModel):
    notification_id: UUID
    status: str

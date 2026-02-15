from sqlalchemy.orm import Session
from models import UserNotificationSettings


def can_send_email(user_id: str, db: Session) -> bool:
    """
    Returns True if user has email notifications enabled.
    If no record exists, default is True (opt-out model).
    """

    setting = (
        db.query(UserNotificationSettings)
        .filter(
            UserNotificationSettings.user_id == user_id,
            UserNotificationSettings.channel == "email",
        )
        .one_or_none()
    )

    # If no row -> default enabled
    if setting is None:
        return True

    return setting.enabled

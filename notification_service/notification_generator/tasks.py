import os
from datetime import datetime, timedelta
import requests
from taskiq import TaskiqDepends, Context

from broker import broker
from analytics import has_events_since
from state import GeneratorState
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('NOTIF_DB_URL')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

NOTIFICATION_API_URL = "http://notification_api:8000/v1/internal/notifications"


@broker.task(schedule=[{"cron": "0 9 * * 1"}])  # Every Monday 09:00
async def weekly_digest(context: Context = TaskiqDepends()):
    """
    Generate weekly digest notification.
    """

    db = SessionLocal()

    try:
        state = db.get(GeneratorState, "weekly_digest")

        if not state:
            state = GeneratorState(
                job_name="weekly_digest",
                last_processed_at=datetime.now() - timedelta(days=7),
                version="v1",
            )
            db.add(state)
            db.commit()

        # Idempotency check
        if not has_events_since(state.last_processed_at):
            return

        payload = {
            "week": datetime.now().strftime("%Y-W%U"),
        }

        response = requests.post(
            NOTIFICATION_API_URL,
            json={
                "event_key": "weekly_digest",
                "target": {
                    "type": "segment",
                    "value": f"weekly_active_{state.version}",
                },
                "payload": payload,
            },
            timeout=5,
        )
        response.raise_for_status()

        # Advance state only after successful creation
        state.last_processed_at = datetime.now()
        db.commit()

    finally:
        db.close()

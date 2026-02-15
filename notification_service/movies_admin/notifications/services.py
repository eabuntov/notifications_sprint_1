import requests
from django.conf import settings
from .jinja_env import env


def render_template(template_str: str, context: dict) -> str:
    template = env.from_string(template_str)
    return template.render(**context)


def send_notification(event_key: str, target_segment: str, payload: dict):
    response = requests.post(
        settings.NOTIFICATION_API_URL,
        json={
            "event_key": event_key,
            "target": {
                "type": "segment",
                "value": target_segment,
            },
            "payload": payload,
        },
        timeout=5,
    )
    response.raise_for_status()

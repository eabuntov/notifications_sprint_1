import json
import os

from kafka import KafkaProducer

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def publish_notification(notification_id: str, priority: str = "high") -> None:
    producer.send(
        "notification.events.high",
        {
            "notification_id": notification_id,
            "priority": priority,
        },
    )
    producer.flush()

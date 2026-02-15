import json
import os

from kafka import KafkaConsumer


KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP")

consumer = KafkaConsumer(
    "notification.events.high",
    "notification.events.bulk",
    bootstrap_servers=KAFKA_BOOTSTRAP,
    group_id="notification-workers",
    enable_auto_commit=False,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

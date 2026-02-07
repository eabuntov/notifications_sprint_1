from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from .broker import broker
from . import tasks  # noqa: F401

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

if __name__ == "__main__":
    scheduler.run()

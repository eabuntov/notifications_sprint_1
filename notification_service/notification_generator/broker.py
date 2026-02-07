from taskiq_redis import RedisBroker

broker = RedisBroker(
    url="redis://notification_redis:6379/1",
)

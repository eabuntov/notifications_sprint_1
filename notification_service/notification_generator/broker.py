from taskiq_redis import RedisStreamBroker

broker = RedisStreamBroker(
    url="redis://notification_redis:6379/1",
)

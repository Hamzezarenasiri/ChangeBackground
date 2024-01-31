import taskiq_fastapi
from taskiq import InMemoryBroker, ZeroMQBroker
from Background_changer.settings import settings
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend
from taskiq_aio_pika import AioPikaBroker
result_backend = RedisAsyncResultBackend(
    redis_url=str(settings.redis_url.with_path("/1")),
)
broker = AioPikaBroker(
    str(settings.rabbit_url),
).with_result_backend(result_backend)

if settings.environment.lower() == "pytest":
    broker = InMemoryBroker()

taskiq_fastapi.init(
    broker,
    "Background_changer.web.application:get_app",
)

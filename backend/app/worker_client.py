from rq import Queue
import redis
from .core.config import settings

redis_conn = redis.from_url(settings.redis_url)
queue = Queue("audio", connection=redis_conn)


def enqueue_audio_job(job_id: str):
    return queue.enqueue("tasks.audio.process_audio_job", job_id)

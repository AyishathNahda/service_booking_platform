import json
import logging
import redis
import time
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_worker():
    redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )

    logger.info("Starting Redis review summary worker...")

    while True:
        try:
            result = redis_client.brpop(
                "review_summary_queue",
                timeout=5
            )

            # No job arrived within 5 seconds.
            # This is normal, so simply continue waiting.
            if not result:
                continue

            queue_name, job_data_str = result
            job_data = json.loads(job_data_str)

            job_id = job_data.get("job_id")
            provider_id = job_data.get("provider_id")

            logger.info(
                f"Processing review summarisation job {job_id}"
            )
            logger.info(f"Provider: {provider_id}")

            # Stub for future LLM summarisation
            time.sleep(2)

            logger.info(f"Completed job {job_id}")

        except redis.exceptions.RedisError as e:
            logger.error(f"Redis error: {e}")
            time.sleep(5)

        except Exception as e:
            logger.error(f"Worker error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    run_worker()
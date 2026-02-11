import json
import os

from redis import Redis


class NewsletterCache:
    def __init__(self, redis_url: str, ttl_seconds: int):
        self.client = Redis.from_url(redis_url, decode_responses=True)
        self.ttl_seconds = ttl_seconds

    def get_summary(self, source_key: str) -> dict | None:
        raw = self.client.get(self._key(source_key))
        if not raw:
            return None
        return json.loads(raw)

    def set_summary(self, source_key: str, summary: dict) -> None:
        payload = json.dumps(summary, ensure_ascii=False)
        self.client.setex(self._key(source_key), self.ttl_seconds, payload)

    @staticmethod
    def _key(source_key: str) -> str:
        return f"newsletter:summary:{source_key}"


def build_cache_from_env() -> NewsletterCache:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise ValueError("REDIS_URL is not set")
    ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "604800"))
    return NewsletterCache(redis_url, ttl_seconds)

import time
from fastapi import HTTPException


class SimpleRateLimiter:
    def __init__(self, limit: int, window_sec: int = 60):
        self.limit = limit
        self.window_sec = window_sec
        self.hits = {}

    def hit(self, key: str):
        now = time.time()
        window_start = now - self.window_sec
        self.hits.setdefault(key, [])
        self.hits[key] = [t for t in self.hits[key] if t >= window_start]
        if len(self.hits[key]) >= self.limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        self.hits[key].append(now)

rate_limiter = SimpleRateLimiter(limit=30, window_sec=60)

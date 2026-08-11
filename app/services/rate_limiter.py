"""
Fixed-window rate limiter backed by Redis.

Algorithm: for each user, maintain a counter key that expires after
WINDOW_SECONDS. Every request does INCR (atomic in Redis — no race
condition even under concurrent requests). If this is the first
request in the window (INCR returns 1), set the key's expiry. If the
counter exceeds the limit, reject.

This is a "fixed window" limiter, not "sliding window" — simpler to
reason about and implement, but has a known edge case worth knowing
for interviews: a user could send LIMIT requests right at the end of
one window and LIMIT more right at the start of the next, briefly
exceeding the intended rate. A sliding-window-log or token-bucket
algorithm fixes that at the cost of more complexity. Naming this
tradeoff explicitly is a good interview answer if asked "how would
you improve this?"
"""

from fastapi import HTTPException, status

from app.redis_client import redis_client

WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 10


def check_rate_limit(user_id: int) -> None:
    key = f"rate_limit:shorten:{user_id}"

    current_count = redis_client.incr(key)

    if current_count == 1:
        # First request in a fresh window — start the clock.
        redis_client.expire(key, WINDOW_SECONDS)

    if current_count > MAX_REQUESTS_PER_WINDOW:
        ttl = redis_client.ttl(key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again shortly.",
            headers={"Retry-After": str(ttl if ttl > 0 else WINDOW_SECONDS)},
        )
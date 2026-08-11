import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# decode_responses=True means we get back Python strs, not bytes —
# simpler to work with for a cache holding plain URLs.
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Cache-aside TTL. 1 hour is a reasonable starting point for a portfolio
# project — tune this and write down your reasoning, it's a good
# interview talking point (hot links vs. cold links, staleness tolerance).
CACHE_TTL_SECONDS = 60 * 60

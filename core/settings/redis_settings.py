from .base_settings import env

# -------------------------------------
# REDIS: envurations
# -------------------------------------
REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env("REDIS_PORT", default="6379")
REDIS_DB = env("REDIS_DB", default="0")
REDIS_PASSWORD = env("REDIS_PASSWORD", default="")

# -------------------------------------
# CHANNELS envURATION
# -------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": (REDIS_HOST, int(REDIS_PORT)),
                    "password": REDIS_PASSWORD or None,
                    "db": int(REDIS_DB),
                }
            ],
        },
    },
}

# -------------------------------------
# CACHE envURATION
# -------------------------------------
if REDIS_PASSWORD:
    _redis_location = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    _redis_location = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": _redis_location,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

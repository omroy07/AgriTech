from flask_caching import Cache

# Configure cache
cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',  # Use simple in-memory cache
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes default
})

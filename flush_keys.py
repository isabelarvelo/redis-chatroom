import redis

r = redis.Redis(host='my-redis', port=6379, decode_responses=True)

# Delete all keys
r.flushall()


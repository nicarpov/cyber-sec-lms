from redis_config import REDIS_HOST, REDIS_PORT, REDIS_DB
import redis

def redis_conn():
    return redis.Redis(REDIS_HOST, REDIS_PORT, REDIS_DB, decode_responses=True)
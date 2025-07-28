from redis_config import REDIS_HOST, REDIS_PORT, REDIS_DB
import redis

def redis_conn():
    return redis.Redis(REDIS_HOST, REDIS_PORT, REDIS_DB, decode_responses=True)

def get_job_state():
    '''
    redis key - "job_state"
    state = {
    'result_id' : uuid,
    'status': loading|ready,
    'lab_id': 123
    }
    '''
    with redis_conn() as conn:
        return conn.hgetall('job_state')
    
def set_job_state(state):
    with redis_conn() as conn:
        return conn.hset('job_state', mapping=state)
    
def flush_job_state():
    with redis_conn() as conn:
        return conn.delete('job_state')
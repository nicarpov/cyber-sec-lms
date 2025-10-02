from redis_config import REDIS_HOST, REDIS_PORT, REDIS_DB
import redis
import json
from remote_control import search_hosts

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
    
def get_platform_state():
    '''
    redis key - "job_state"
    state = {
    'result_id' : uuid,
    'status': loading|ready,
    'lab_id': 123
    }
    '''
    with redis_conn() as conn:
        return conn.hgetall('platform_state')
    
def set_platform_state(state):
    with redis_conn() as conn:
        return conn.hset('platform_state', mapping=state)
    
def set_job_state(state):
    with redis_conn() as conn:
        return conn.hset('job_state', mapping=state)
    
def flush_job_state():
    with redis_conn() as conn:
        return conn.delete('job_state')
    
def get_hosts_state():
    '''
    redis key - "hosts_state"
    state = {
        'result_id'
        'hosts_online': list
    }
    '''
    with redis_conn() as conn:
        return conn.hgetall('hosts_state')
    
def set_hosts_state(state):
    with redis_conn() as conn:
        return conn.hset('hosts_state', mapping=state)
    
def flush_hosts_state():
    with redis_conn() as conn:
        return conn.delete('hosts_state')
    
def get_unreg_hosts():
    '''
    redis key - "hosts_state"
    state = {
        'result_id'
        'hosts_online': list
    }
    '''
    with redis_conn() as conn:
        res = conn.get('unreg_hosts')
        if res:
            return json.loads(res)
        else:
            return []
    
def set_unreg_hosts(hosts):
    with redis_conn() as conn:
        return conn.set('unreg_hosts', value=json.dumps(hosts))
    



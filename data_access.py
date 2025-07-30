from redis_config import REDIS_HOST, REDIS_PORT, REDIS_DB
import redis
import json

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
    
def get_hosts_state_id():
    '''
    redis key - "hosts_state"
    state = {
        'result_id'
        'hosts_online': list
    }
    '''
    with redis_conn() as conn:
        return conn.get('hosts_state_id')
    
def set_hosts_state_id(id):
    with redis_conn() as conn:
        return conn.set('hosts_state_id', value=id)
    
def flush_hosts_state_id():
    with redis_conn() as conn:
        return conn.delete('hosts_state_id')
    
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
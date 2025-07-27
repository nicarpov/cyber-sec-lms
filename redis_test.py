from app.data_access import redis_conn

with redis_conn() as conn:
    conn.delete('job_state')
    d = conn.hgetall('job_state')
    print(d)

    


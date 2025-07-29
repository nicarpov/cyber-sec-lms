from celery import Celery, group

import time
from celery.result import AsyncResult, GroupResult
from celeryconfig import CELERY
from remote_control import reboot, isAvailable, search_hosts
from remote_ctl_config import RemoteCtlConf
# PKEY_PATH, SUDO_PASS, REMOTE_USER, REMOTE_PORT, BACKUP_DIR


celery_app = Celery('tasks', 
            # broker='pyamqp://guest@192.168.0.134/', 
            # broker='redis://192.168.0.134:6379/0',
            # backend='rpc://',
            
            )

celery_app.config_from_object(CELERY)


@celery_app.task()
def add(x, y):
    sum = (x + y)
    duration = sum
    time.sleep(duration)
    
    
    return sum

@celery_app.task()
def task_reboot(host):
    r = reboot(host)
    return r

@celery_app.task
def backup(host: str, comment: str, path: str, link: str = None):
    time.sleep(3)
    return {"backup_id": 1,
            "host": host,
            "comment": comment,
            }

@celery_app.task
def restore(host: str, backup_id: str):
    time.sleep(3)
    
    return {"backup_id": backup_id,
            "host": host,
            }

@celery_app.task
def task_isOnline(host):
    return isAvailable(host)

@celery_app.task
def task_search_hosts(nmap_target):
    res = search_hosts(nmap_target=nmap_target)
    return res

def allIsDone(groupResId):
    try:
        groupRes = GroupResult.restore(groupResId, app=celery_app)
        results = groupRes.results
        tasks_num = len(results)
        ready_num = len(list(filter(lambda t: t.ready(), results)))
        return ready_num == tasks_num
    except Exception as err:
        print("allIsDone Error:", err)
        return False
    

if __name__ == "__main__":
    # g = group([task_reboot.s('localhost') for i in range(4)])
    # r = g.delay()
    r = task_search_hosts.apply_async(args=['192.168.0.0/24'])
    print(r.get())





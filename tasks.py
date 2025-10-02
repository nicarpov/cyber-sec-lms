from celery import Celery, group
from celery.schedules import crontab

import time
from celery.result import AsyncResult, GroupResult
from celeryconfig import CELERY
from remote_control import reboot, isAvailable, search_hosts, backup, restore, backup_routeros, restore_routeros, run_cmd_set
from data_access import set_unreg_hosts, get_unreg_hosts
from remote_ctl_config import RemoteCtlConf as rconf

# PKEY_PATH, SUDO_PASS, REMOTE_USER, REMOTE_PORT, BACKUP_DIR


celery_app = Celery('tasks', 
            # broker='pyamqp://guest@192.168.0.134/', 
            # broker='redis://192.168.0.134:6379/0',
            # backend='rpc://',
            
            )

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(10.0, task_search_hosts.s(rconf.SUBNET), name="Search hosts")

celery_app.config_from_object(CELERY)



# celery_app.conf.beat_schedule = {
#     'search-hosts-every-10-seconds': {
#         'task': 'tasks.task_search_hosts',
#         'schedule': 10.0,
#         'args': (rconf.SUBNET)
#     },
# }
celery_app.conf.timezone = 'UTC'

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

@celery_app.task()
def task_backup(host: str, backup_uid: str, link: str = None):
    # return add(5, 5)
    return backup(host=host, backup_uid=backup_uid, backup_dir=rconf.BACKUP_DIR, mocked=rconf.MOCKED)

@celery_app.task()
def task_backup_routeros(host: str, backup_uid: str, link: str = None):
    # return add(5, 5)
    return backup_routeros(host=host, backup_uid=backup_uid, backup_dir=rconf.BACKUP_DIR)
    

@celery_app.task()
def task_restore(host: str, backup_id: str, autoreboot: bool, preset: list):
    # return add(5,5)
    return restore(host, backup_id, autoreboot=autoreboot, mocked=rconf.MOCKED, preset=preset)

@celery_app.task()
def task_restore_routeros(host: str, backup_id: str):
    # return add(5,5)
    return restore_routeros(host, backup_id)  
    

@celery_app.task()
def task_isOnline(host):
    return isAvailable(host)

@celery_app.task()
def task_search_hosts(nmap_target):
    
    unreg_hosts = search_hosts(nmap_target=nmap_target) 
    
    
    
    set_unreg_hosts(unreg_hosts)
    return unreg_hosts

@celery_app.task()
def task_run_cmd_set(host, set):
    
    return run_cmd_set(host, set)

def allIsDone(results):
    try:
        
        
        print("res", results)
        print("3")
        tasks_num = len(results)
        print("4")
        ready_num = len(list(filter(lambda t: t.ready(), results)))
        print("5")
        return ready_num == tasks_num
    except Exception as err:
        print("allIsDone Error:", err)
        return {"error": str(err)}

def job_results(results):
    try:
        
        results = [r.get() for r in results]
        
        return results
    except Exception as err:
        
        return {'err': repr(err)}
    


if __name__ == "__main__":
    # g = group([add.s(1,2) for i in range(4)])
    # r = g.delay()
    # r.save()
    # print(r.id)


    # r = task_search_hosts.apply_async(args=['192.168.0.0/24'])
    # print(allIsDone('2a6d3251-e897-4aef-92e5-92af9d050a24'))


    # tasks = []
    # for i in range(10):
    #     tasks.append(add.s(i,i))
    # task_group = group(tasks)
    # r = task_group.delay()
    # r.save()
    # print(r.id)


    res = GroupResult.restore('bdbab130-53c0-4c75-9457-334c35c30f17', app=celery_app)
    print(res)
    ready = allIsDone(res.results)
    print(ready)





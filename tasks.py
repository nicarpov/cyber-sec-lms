from celery import Celery, group
import time
from celery.result import AsyncResult, GroupResult
from celeryconfig import CELERY





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
    # hosts = [1, 2, 3, 4]
    # backup_ids = [ 2, 3, 4, 5]
    # job = group([add.s(host, id) for host, id in zip(hosts, backup_ids)])
    # r = job.delay()
    # print(r.id)
    # r.save()
    # restored = GroupResult.restore(r.id)
    
    # print('res type:', type(res.results))
    id = "75dac67a-49b5-4b67-95c2-41b196fe6704"
    while not allIsDone(groupResId=id):
        time.sleep(1)
        continue
    print(id, 'Is Done')



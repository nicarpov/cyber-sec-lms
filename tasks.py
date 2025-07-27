from celery import Celery
import time
from celery.result import AsyncResult
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

if __name__ == "__main__":
    task = add.delay(1, 1)
    print(task.id)
    
    # result = AsyncResult(id=task.id)
    # result = AsyncResult(id='7880d386-3393-42bb-85e5-aff10d06c6eb')
    # print(f"Task ID: {result.id}")
    
    # # print(result.state)
    # # while result.state != 'SUCCESS' :
    # #     continue
    # print(result.result)



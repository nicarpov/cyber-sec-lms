from celery import Celery
import time

celery_app = Celery('app.tasks', 
            broker='pyamqp://guest@192.168.0.134//', 
            backend='rpc://',
            
            )

@celery_app.task()
def add(x, y):
    sum = (x + y) * 10
    duration = sum
    time.sleep(duration)
    
    
    return sum




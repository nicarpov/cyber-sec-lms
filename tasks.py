from celery import Celery
import time

app = Celery('tasks', 
            broker='pyamqp://guest@192.168.0.134//', 
            backend='rpc://',
            
            )

@app.task()
def add(x, y, duration=5):
    
    time.sleep(duration)
    sum = (x + y) * 10
    
    return sum

@app.task()
def notify(sum):

    return "Sum calculated {}".format(sum)


def on_raw_message(body):
    print(body)


def main():
    r = add.apply_async((2,2,3), link=notify.s())
    


if __name__ == '__main__':
    main()

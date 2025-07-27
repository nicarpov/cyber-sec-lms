from app import app
from flask import render_template, redirect, url_for
from app.forms import EmptyForm
from app.models import labs, current_lab, task_id, hosts
from app import sock
from tasks import celery_app, add, backup, restore
from celery import group
from celery.result import AsyncResult
from test_app import MOCKED
from uuid import uuid4
import time
import json
from app.data_access import redis_conn

@app.route('/')
@app.route('/index')
def index():
    
    # form = EmptyForm()
    lab_list = []
    for id in labs:
        lab = labs[id]
        lab['id'] = id
        lab_list.append(lab)
    return render_template('index.html', labs=lab_list)



@app.route('/lab/backup/<lab_id>', methods=['POST'])
def lab_backup(lab_id):
    # lab['id'] = lab_id
    form = EmptyForm()
    
    if form.validate_on_submit:
        comment = "TEST"
        if MOCKED:
            r_id = str(uuid4())
            task_id.append(r_id)
        else:
            job = group(backup.s(host, comment) for host in hosts)
            r = job.delay()
            task_id.append(r.id)
        return redirect(url_for('lab_room', lab_id=lab_id))


@app.route('/lab/start/<lab_id>', methods=['POST'])
def lab_start(lab_id):

    form = EmptyForm()
    if form.validate_on_submit:
            
        # backup_ids = ["123", "234", "345"] # TO-DO: get hosts backup ids for lab 
        if MOCKED:
            hosts = [1, 2, 3, 4]
            backup_ids = [ 2, 3, 4, 5]
            job = group([add.s(host, id) for host, id in zip(hosts, backup_ids)])
            r = job.delay()
            
            with redis_conn() as conn:
                conn.hset('job_state', mapping={
                    'result_id': r.id,
                    'status': 'loading',
                    'lab_id': str(lab_id)
                })
            
        else:
            # job = group([restore.s(host, id) for host, id in zip(hosts, backup_ids)])
            # r = job.delay()
            # task_id.append(r.id)
            
            # if нет задач backup и restore:
            #   1. Получить список хосты и пути к бекапам для лабы с данным id включая сам ноут
            #   2. Отправить на celery группу задач по восстановлению бекапов
            #   3. Положить id задачи в redis
            pass
        form = EmptyForm()
        return redirect(url_for('lab_room', lab_id=lab_id))

@app.route('/lab/finish/<lab_id>', methods=['POST'])
def lab_finish(lab_id):
    
    form = EmptyForm()
    if form.validate_on_submit:
            global current_lab
            current_lab = {}
            return redirect(url_for('lab_room', lab_id=lab_id))

# @app.route('/lab_manual/<lab_id>')
# def lab_manual(lab_id):

#     return render_template('lab_manual.html', manual_link=link)

@app.route("/lab/room/<lab_id>")
def lab_room(lab_id):
    # lab['id'] = lab_id
    
    lab = labs[lab_id]
    lab['id'] = lab_id
    
    form = EmptyForm()
    return render_template("lab_room.html", lab=lab, form=form, current_lab=current_lab)

@app.route("/lab/manual/<lab_id>")
def lab_manual(lab_id):
    # lab['id'] = lab_id
    
    lab = labs[lab_id]
    lab['id'] = lab_id
    
    form = EmptyForm()
    return render_template("lab_manual.html", lab=lab, form=form, current_lab=current_lab)



@sock.route('/ws/job_state')
def job_state(ws):
    '''
    redis key - "job_state"
    state = {
    'result_id' : uuid,
    'status': loading|ready,
    'lab_id': 123
    }
    '''
    state = {}
    
    with redis_conn() as conn:
        state = conn.hgetall('job_state')
        print(state)
        if state:
            result_id = state['result_id']
            r = celery_app.AsyncResult(result_id)
            status = ''
            if r.ready():
                conn.delete('job_state')
                status = 'ready'
                
            else:
                status = 'loading'
            state['status'] = status
            
            
    ws.send(json.dumps(state))
    while True:
        time.sleep(1)
        if state:
            result_id = state['result_id']
            r = celery_app.AsyncResult(result_id)
            status = ''
            # print(r.state)
            if r.ready():
                print("READY")
                with redis_conn() as conn:
                    conn.delete('job_state')
                status = 'ready'
                state['status'] = status
                ws.send(json.dumps(state))
            
            

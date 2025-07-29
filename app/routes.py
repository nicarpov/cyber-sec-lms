from app import app
from flask import render_template, redirect, url_for
from app.forms import EmptyForm
from app.models import labs, current_lab, task_id, hosts, Host, Lab, Backup
import sqlalchemy as sa
from app import db
from app import sock
from tasks import celery_app, allIsDone, add, backup, restore, task_reboot
from celery import group
from celery.result import AsyncResult
from test_app import MOCKED
from uuid import uuid4
import time
import json
from data_access import redis_conn, get_job_state, set_job_state


# MAIN ROUTES
@app.route('/')
@app.route('/index')
def index():
    state = get_job_state()
        
    if state:
        return redirect(url_for('lab_room', lab_id=state['lab_id']))

    lab_list = []
    for id in labs:
        lab = labs[id]
        lab['id'] = id
        lab_list.append(lab)
    return render_template('index.html', labs=lab_list)

@app.route('/login')
def login():
    form = EmptyForm()
    if form.validate_on_submit():
        # login code
        user_id = 1
        return redirect(url_for('user', user_id=user_id))
    
    return render_template('login.html', form=form)
    
@app.route('/admin')
def admin():
    global labs
    global hosts
    for host in hosts:
        host['connected'] = True
    lab_list = []
    for id in labs:
        lab = labs[id]
        lab['id'] = id
        lab_list.append(lab)
    return render_template('admin.html', labs=lab_list, hosts=hosts)

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
    
    while True:
        
        state = get_job_state()
        if state:
            
            status = state['status']
            if status == 'loading':
                result_id = state['result_id']
                
                status = ''
                
                if allIsDone(result_id):
                    status = 'ready'
                    state['status'] = status
                    set_job_state(state)
                    
        ws.send(json.dumps(state))
        time.sleep(1)

@app.route("/reboot", methods=['POST'])
def reboot():
    state = get_job_state()
    
    form = EmptyForm()
    if form.validate_on_submit():
        if state:
            state['status'] = 'reboot'
            set_job_state(state)
            
            task_reboot.apply_async(args=['127.0.0.1'], countdown=5)
            return redirect(url_for('lab_room', lab_id=state['lab_id']))
        else:
            return redirect(url_for('index'))

# LAB ROUTES
@app.route('/lab/create', methods=['GET', 'POST'])
def lab_create():
    return render_template('lab_create.html')

@app.route('/lab/control/<lab_id>')
def lab_control(lab_id):
    global labs
    lab = labs[lab_id]
    lab['id'] = lab_id
    return render_template('lab_control.html', lab=lab)

@app.route('/lab/edit/<lab_id>', methods=['GET', 'POST'])
def lab_edit(lab_id):
    global labs
    lab = labs[lab_id]
    return render_template('lab_edit.html', lab=lab)

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
            r.save()
            set_job_state({
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

# HOST ROUTES
@app.route("/host/create", methods=['GET', 'POST'])
def host_create():
    return render_template('host_create.html')

@app.route("/host/edit", methods=['GET', 'POST'])
def host_edit():
    return render_template('host_edit.html')

@app.route("/host/control/<host_id>")
def host_control(host_id):
    global hosts
    host = hosts[0]
    return render_template('host_control.html', host=host)



# @app.route('/lab_manual/<lab_id>')
# def lab_manual(lab_id):

#     return render_template('lab_manual.html', manual_link=link)







                
            

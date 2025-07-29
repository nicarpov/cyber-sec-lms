from app import app
from flask import render_template, redirect, url_for, flash
from app.forms import EmptyForm, HostCreate, LabCreate
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
    labs = db.session.scalars(sa.select(Lab).order_by(Lab.name)).all()
    hosts = db.session.scalars(sa.select(Host).order_by(Host.name)).all()
    
    
    return render_template('admin.html', labs=labs, hosts=hosts)

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
    form = LabCreate()
    if form.validate_on_submit():
        lab = Lab(name=form.name.data)
        db.session.add(lab)
        db.session.commit()
        flash('Лабораторная работа успешно создана: {}'.format(lab.name))
        return redirect(url_for('admin'))
    return render_template('lab_create.html', form=form)

@app.route('/lab/control/<lab_id>')
def lab_control(lab_id):
    lab = db.session.get(Lab, int(lab_id))
    form = EmptyForm()
    return render_template('lab_control.html', lab=lab, form=form)

@app.route('/lab/edit/<lab_id>', methods=['GET', 'POST'])
def lab_edit(lab_id):
    lab =  db.session.get(Lab, int(lab_id))
    form = LabCreate()
    if form.validate_on_submit():
        lab.name = form.name.data
        db.session.commit()
        flash("Изменения успешно сохранены")
        return redirect(url_for('lab_control', lab_id=lab_id))
    form.name.data = lab.name
    return render_template('lab_edit.html', lab=lab, form=form)

@app.route('/lab/delete/<lab_id>', methods=['POST'])
def lab_delete(lab_id):
    form = EmptyForm()
    if form.validate_on_submit():
        
        lab = db.session.get(Lab, int(lab_id))
        if lab:
            db.session.delete(lab)
            db.session.commit()
            flash("Лабораторная работа удалена: {}".format(lab.name))
            return redirect(url_for('admin'))
        else:
            flash("Данных о работе не обнаружено. ID работы: ".format(lab_id))
            return redirect(url_for('lab_control'))
    return redirect(url_for('admin'))

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
    form = HostCreate()
    if form.validate_on_submit():
        host = Host(name=form.name.data, ip=form.ip.data)
        db.session.add(host)
        db.session.commit()
        flash("Успешно зарегистрирован хост: {} IP: {}".format(host.name, host.ip))
        return redirect(url_for('admin'))
    
    return render_template('host_create.html', form=form)

@app.route("/host/edit", methods=['GET', 'POST'])
def host_edit():
    return render_template('host_edit.html')

@app.route("/host/delete/<host_id>", methods=['POST'])
def host_delete(host_id):
    form = EmptyForm()
    if form.validate_on_submit():
        host = db.session.get(Host, int(host_id))
        if host:
            db.session.delete(host)
            db.session.commit()
            flash("Данные о хосте успешно удалены: {}".format(host.ip))
        else:
            flash("Данные хоста с id {} не обнаружены".format(host_id))
    return redirect(url_for('admin'))

@app.route("/host/control/<host_id>")
def host_control(host_id):
    form = EmptyForm()
    host = db.session.get(Host, int(host_id))
    return render_template('host_control.html', host=host, form=form)








                
            

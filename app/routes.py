import os
from app import app
from flask import render_template, redirect, url_for, flash, request
from app.forms import EmptyForm, HostCreate, LabCreate
from app.models import labs, current_lab, task_id, hosts, Host, Lab, Backup, Save
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from app import db
from app import sock
from tasks import celery_app, allIsDone, add, task_backup, task_restore, task_reboot, task_search_hosts, \
    task_backup_routeros, task_restore_routeros, job_results
from celery import group
from celery.result import AsyncResult, GroupResult
from test_app import MOCKED
from uuid import uuid4
import time
import json
from data_access import get_job_state, set_job_state, flush_job_state, \
get_unreg_hosts
from remote_ctl_config import RemoteCtlConf as rconf
from remote_control import backup_remove
web_socks = []

# MAIN ROUTES
@app.route('/')
@app.route('/index')
def index():
    state = get_job_state()
        
    if state:
        return redirect(url_for('lab_room', lab_id=state['lab_id']))

    lab_list = db.session.scalars(sa.select(Lab).where(Lab.hidden == False).order_by(Lab.name))
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
    
    discovered_hosts = get_unreg_hosts() 
    unreg_hosts = []

    for host in discovered_hosts:
        reg_host = db.session.scalar(sa.select(Host).where(Host.ip == host))
        if not reg_host:
            unreg_hosts.append(host)
    
    state = get_job_state()
    if state and state['status'] == ['ready', 'error']:
        flush_job_state()

    form = EmptyForm()
    return render_template('admin.html', labs=labs, hosts=hosts, unreg_hosts=unreg_hosts, form=form)

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
    i = 0
    results = {}
    while True:
        
        state = get_job_state()
        print("Get state")
        print(state) 
        if state:
            print("State ", i)
            
            status = state['status']
            if status == 'loading':
                result_id = state['result_id']
                if not results:
                    results = GroupResult.restore(result_id, backend=celery_app.backend)
                
                status = ''
                print("Before allIsdone")
                print("id", result_id)
                done = allIsDone(results.results)
                print("DONE:", done)
                if done:
                    print("Inside allIsdone")
                    print("DONE:", done)
                    res = job_results(result_id)
                    
                    print('results: ', res, 'result type', type(res))
                    errors = []
                    for r in res:
                        if type(r) == dict:
                            if 'err' in r.keys():
                                err = f"Хост: {r['host']} -> {r['err']}"
                                errors.append(err)
                                status = 'error'
                            
                    if status != 'error':
                        status = 'ready'
                    else:
                        print("Send errors")
                        state['err'] = json.dumps(errors)

                    state['status'] = status
                    set_job_state(state)
                    
          
        ws.send(json.dumps(state))
        time.sleep(1)
        print(i)
        i += 1

# @sock.route('/ws/hosts_state')
# def hosts_state(ws):
#     '''
#     redis key - "hosts_state"
#     state = {
    
#     }
#     '''
#     web_socks.append(ws)
#     while True:
#         task_state = get_hosts_state()
#         # print(task_state)
#         if task_state:
#             res = AsyncResult(task_state['id'], app=celery_app)
#             if res.ready():
#                 hosts = res.get()
#                 registered_hosts = []
#                 unreg_hosts = []
#                 for host in hosts:
#                     reg_host = db.session.scalar(sa.select(Host).where(Host.ip == host))
#                     if reg_host:
#                         registered_hosts.append(host)
#                     else:
#                         unreg_hosts.append(host)
                
#                 # ws.send(json.dumps(state))
#                 set_unreg_hosts(unreg_hosts)
#             t1 = int(time.time())
#             t0 = int(get_hosts_state()['sent_time'])
#             if t1 - t0 > 10:
#                 print('t0: ', t0, 't1: ', t1)
#                 t0 = t1
#                 task = task_search_hosts.apply_async(args=[rconf.SUBNET])
#                 print("Task sent main", task.id)
                
#                 set_hosts_state({'id': task.id, 'sent_time': t1})
                
#         else:
#             task = task_search_hosts.apply_async(args=[rconf.SUBNET])
#             t0 = int(time.time())
            
#             set_hosts_state({'id': task.id, 'sent_time': t0})
    
        
            

@app.route("/reboot", methods=['POST'])
def reboot():
    state = get_job_state()
    
    form = EmptyForm()
    if form.validate_on_submit():
        if state:
            state['status'] = 'reboot'
            set_job_state(state)
            
            task_reboot.apply_async(args=['127.0.0.1'])
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
    saves = db.session.scalars(sa.select(Save)
                               .where(Save.lab_id == int(lab_id)).order_by(Save.timestamp)).all()
    
    
    state = get_job_state()
    if state and state['status'] in ['ready', 'error']:
        flush_job_state()
    return render_template('lab_control.html', lab=lab, form=form, saves=saves)

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
            query = lab.saves.select()
            saves = db.session.scalars(query).all()
            for save in saves:
                query = save.backups.select()
                backups = db.session.scalars(query).all()
                for backup in backups:
                    db.session.delete(backup)
                db.session.delete(save)
            db.session.delete(lab)
            db.session.commit()
            print('Saves count: ', db.session.query(Save).count())
            flash("Лабораторная работа удалена: {}".format(lab.name))
            return redirect(url_for('admin'))
        else:
            flash("Данных о работе не обнаружено. ID работы: ".format(lab_id))
            return redirect(url_for('lab_control'))
    return redirect(url_for('admin'))




@app.route('/lab/start/<lab_id>', methods=['POST'])
def lab_start(lab_id):
    form = EmptyForm()
    lab = db.session.get(Lab, int(lab_id))
    # save = db.session.scalar(sa.select(Save).where(Save.is_default == True))
    save_query = lab.saves.select().where(Save.is_default == True)
    save = db.session.scalar(save_query)
    
    if form.validate_on_submit:
        if save:
            backups = db.session.scalars(save.backups.select()).all()
            if backups:
                task_list = []
                for backup in backups:
                    if backup.host.os_type == 'linux':
                        autoreboot = True
                        if backup.host.name == 'localhost' or backup.host.ip == '127.0.0.1':
                            autoreboot = False
                        task_list.append(task_restore.s(host=backup.host.ip, backup_id=backup.uid, autoreboot=autoreboot))
                    elif backup.host.os_type == 'routeros':
                        task_list.append(task_restore_routeros.s(backup.host.ip, backup.uid))
                
                task_group = group(task_list)
                r = task_group.delay()
                r.save()
                set_job_state({
                        'job_type': 'load',
                        'result_id': r.id,
                        'status': 'loading',
                        'lab_id': str(lab_id)
                    })

            else:
                flash("Ошибка! Нет бекапов для загрузки точки сохранения")
        else:
            flash("Ошибка! Нет точек сохранения")
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
    
    lab = db.session.get(Lab, int(lab_id))
    
    form = EmptyForm()
    return render_template("lab_room.html", lab=lab, form=form)

@app.route("/lab/manual/<lab_id>")
def lab_manual(lab_id):
    # lab['id'] = lab_id
    
    lab = labs[lab_id]
    lab['id'] = lab_id
    
    form = EmptyForm()
    return render_template("lab_manual.html", lab=lab, form=form, current_lab=current_lab)

@app.route('/lab/hide/<lab_id>', methods=['POST'])
def lab_hide(lab_id):
    form = EmptyForm()
    
    if form.validate_on_submit():
        lab = db.session.get(Lab, int(lab_id))
        lab.hide()
        print("HIdden ",lab.hidden)
        db.session.commit()
        flash("Изменена видимость лабораторной работы: {}".format(lab.name))
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))

@app.route('/lab/show/<lab_id>', methods=['POST'])
def lab_show(lab_id):
    form = EmptyForm()
    
    if form.validate_on_submit():
        lab = db.session.get(Lab, int(lab_id))
        lab.show()
        print("HIdden ",lab.hidden)
        db.session.commit()
        

        flash("Изменена видимость лабораторной работы: {}".format(lab.name))
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))

# HOST ROUTES
@app.route("/host/create", methods=['GET', 'POST'])
def host_create():
    form = HostCreate()
    if form.validate_on_submit():
        host = Host(name=form.name.data, ip=form.ip.data, os_type=form.os.data)
        db.session.add(host)
        db.session.commit()
        flash("Успешно зарегистрирован хост: {} IP: {}".format(host.name, host.ip))
        return redirect(url_for('admin'))
    return render_template('host_create.html', form=form)

@app.route("/host/create/<ip>", methods=['GET'])
def host_create_fast(ip):
    form = HostCreate()
    form.ip.data = ip
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
            query = host.backups.select()
            backups = db.session.scalars(query).all()
            for backup in backups:
                db.session.delete(backup)
            db.session.delete(host)
            db.session.commit()
            print('Backups count: ', db.session.query(Backup).count())
            flash("Данные о хосте успешно удалены: {}".format(host.ip))
        else:
            flash("Данные хоста с id {} не обнаружены".format(host_id))
    return redirect(url_for('admin'))

@app.route("/host/control/<host_id>")
def host_control(host_id):
    form = EmptyForm()
    host = db.session.get(Host, int(host_id))
    return render_template('host_control.html', host=host, form=form)

# SAVES ROUTES
@app.route('/save/create/<lab_id>', methods=['POST'])
def save_create(lab_id):
    
    form = EmptyForm()
    
    if form.validate_on_submit:
        hosts = db.session.scalars(sa.select(Host)).all()
        if hosts:
            lab = db.session.get(Lab, int(lab_id))
            save = Save(lab=lab, comment=lab.name, uid=str(uuid4()))
            
            db.session.add(save)
            save.validate_default()
            print('Backups count: ', db.session.query(Backup).where(Backup.save_id == save.id).count())
            
            task_list = []
            for host in hosts:
                backup_uuid = str(uuid4())
                print("Host ",host.ip, "buid ", backup_uuid)
                backup = Backup(save=save, host=host, comment=lab.name, uid=backup_uuid, dir=rconf.BACKUP_DIR)
                db.session.add(backup)
                if host.os_type == 'linux':
                    task_list.append(task_backup.s(host.ip, backup.uid))
                elif host.os_type == 'routeros':
                    task_list.append(task_backup_routeros.s(host.ip, backup.uid))
            task_group = group(task_list)
            r = task_group.delay()
            
            
            try:
                r.save()
            except AttributeError as err:
                flash("AttributeError in save_create")
                return redirect(url_for('lab_control', lab_id=lab_id))
            set_job_state({
                    'job_type': 'save',
                    'result_id': r.id,
                    'status': 'loading',
                    'lab_id': str(lab_id)
                })
            
            db.session.commit()
        else:
            flash("Ошибка! Нет хостов для создания точки сохранения")
    
    return redirect(url_for('lab_control', lab_id=lab_id))

@app.route('/save/delete/<save_id>', methods=['POST'])
def save_delete(save_id):
    form = EmptyForm()
    
    if form.validate_on_submit():
        save = db.session.get(Save, int(save_id))
        lab_id = save.lab_id
        query = save.backups.select()
        backups = db.session.scalars(query).all()
        
        for backup in backups:
            if backup.host.os_type == "linux":
                res = backup_remove(backup.host.ip, backup.uid)
                if not res['cmd_code']:
                    db.session.delete(backup)
                else:
                    flash(f"Ошибка при удалении бекапа: {backup.host.ip} -> {backup.uid}")
        db.session.delete(save)
        db.session.commit()
        # print('Backups count: ', db.session.query(Backup).where(Backup.save_id == save.id).count())
        flash("Точка сохранения успешно удалена: {}".format(save.comment))
        return redirect(url_for('lab_control', lab_id=lab_id))
    return redirect(url_for('lab_control', lab_id=lab_id))

@app.route('/save/restore/<save_id>', methods=['POST'])
def save_restore(save_id):
    form = EmptyForm(save_id)
    
    save = db.session.get(Save, int(save_id))
    lab_id = save.lab_id
    print("Save restore ", save_id, " lab id ", lab_id)
    if form.validate_on_submit:
        backups = db.session.scalars(save.backups.select()).all()
        # print(backups)
        if backups:
            task_list = []
            for backup in backups:
                if backup.host.os_type == 'linux':
                    autoreboot = True
                    if backup.host.name == 'localhost' or backup.host.ip == '127.0.0.1':
                        autoreboot = False
                    task_list.append(task_restore.s(backup.host.ip, backup.uid, autoreboot=autoreboot))
                elif backup.host.os_type == 'routeros':
                    task_list.append(task_restore_routeros.s(backup.host.ip, backup.uid))
                
            task_group = group(task_list)
            r = task_group.delay()
            r.save()
            set_job_state({
                    'job_type': 'load',
                    'result_id': r.id,
                    'status': 'loading',
                    'lab_id': str(lab_id)
                })

        else:
            flash("Ошибка! Нет бекапов для загрузки точки сохранения")
    return redirect(url_for('lab_control', lab_id=lab_id))

@app.route('/save/default/<save_id>', methods=['POST'])
def save_default(save_id):
    form = EmptyForm()
    
    if form.validate_on_submit():
        save = db.session.get(Save, int(save_id))
        
        save.set_default()
        db.session.add(save)
        lab_id = save.lab_id
        db.session.commit()
        print("Save is default", save.is_default)
        flash("Установлена точка сохранения по умолчанию: {}".format(save.comment))
        return redirect(url_for('lab_control', lab_id=lab_id))
    return redirect(url_for('lab_control', lab_id=lab_id))








                
            

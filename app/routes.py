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

@app.route('/')
@app.route('/index')
def index():
    form = EmptyForm()

    return render_template('index.html', labs=labs, form=form)


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
    print(f"LAB ID: {lab_id}")
    f = lambda l: int(l['id']) == int(lab_id)
    current_lab = list(filter(f, labs))[0]
    print(current_lab)
    form = EmptyForm()
    if form.validate_on_submit:
            current_lab['started'] = True
            backup_ids = ["123", "234", "345"] # TO-DO: get hosts backup ids for lab 
            if MOCKED:
                r_id = str(uuid4())
                task_id.append(r_id)
                print("Task ID added: ", r_id)
            else:
                job = group([restore.s(host, id) for host, id in zip(hosts, backup_ids)])
                r = job.delay()
                task_id.append(r.id)
            return redirect(url_for('lab_room', lab_id=lab_id))

@app.route('/lab/finish/<lab_id>', methods=['POST'])
def lab_finish(lab_id):
    
    form = EmptyForm()
    if form.validate_on_submit:
            current_lab['started'] = False 
            return redirect(url_for('lab_room', lab_id=lab_id))

# @app.route('/lab_manual/<lab_id>')
# def lab_manual(lab_id):

#     return render_template('lab_manual.html', manual_link=link)

@app.route("/lab/room/<lab_id>")
def lab_room(lab_id):
    # lab['id'] = lab_id
    lab = labs[0]
    return render_template("lab_room.html", lab=lab)

@sock.route('/ws/message')
def message(ws):
    
    while True:
        
        msg = ws.receive()
        if msg == "WAITING":
            print("WAITING")
            
            while task_id:
                id = task_id[-1]

                if MOCKED:
                    time.sleep(10)
                    task_id.remove(id)
                else:
                    r = AsyncResult(id=id, app=celery_app)
                    if r.ready():
                        task_id.remove(id)

            print("READY")
            ws.send("READY")

    

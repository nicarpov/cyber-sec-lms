from app import app
from flask import render_template, redirect, url_for
from app.forms import EmptyForm
from app.models import lab
from app import sock
from app.tasks import add


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/labs', methods=['GET'])
def labs():
    
    form = EmptyForm()

    return render_template('labs.html', lab=lab, form=form)

@app.route('/lab/start/<lab_id>', methods=['POST'])
def lab_start(lab_id):
    lab['id'] = lab_id
    form = EmptyForm()
    if form.validate_on_submit:
            lab['started'] = True 
            r = add.apply_async((1, 2))
            return redirect(url_for('lab_room', lab_id=lab_id))

@app.route('/lab/finish/<lab_id>', methods=['POST'])
def lab_finish(lab_id):
    
    form = EmptyForm()
    if form.validate_on_submit:
            lab['started'] = False 
            return redirect(url_for('lab_room', lab_id=lab_id))

# @app.route('/lab_manual/<lab_id>')
# def lab_manual(lab_id):

#     return render_template('lab_manual.html', manual_link=link)

@app.route("/lab/room/<lab_id>")
def lab_room(lab_id):
    lab['id'] = lab_id
    return render_template("lab_room.html", lab=lab)

@sock.route('/ws/message')
def message(ws):
    
    while True:
        
        msg = ws.receive()
        if msg == "WAITING":
            
            # while not r.ready():
            #     continue
            ws.send("READY")

    

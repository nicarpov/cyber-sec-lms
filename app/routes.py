from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/labs')
def labs():
    lab = {
        "id": 1,
        "name": "ЛР1.1",
    }
    return render_template('labs.html', lab=lab, form=form)

@app.route('/lab_manual/<lab_id>')
def lab_manual(lab_id):

    return render_template('lab_manual.html', manual_link=link)
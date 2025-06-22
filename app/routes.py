from app import app
from flask import render_template, redirect, url_for
from app.forms import EmptyForm
from app.models import lab

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/labs')
def labs():
    
    form = EmptyForm()

    return render_template('labs.html', lab=lab, form=form)

@app.route('/lab_start/<lab_id>', methods=['POST'])
def lab_start(lab_id):
    
    form = EmptyForm()
    if form.validate_on_submit:
            lab['started'] = True 
    return redirect(url_for('labs', lab=lab))
# @app.route('/lab_manual/<lab_id>')
# def lab_manual(lab_id):

#     return render_template('lab_manual.html', manual_link=link)
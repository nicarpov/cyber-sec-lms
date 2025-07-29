from flask import Flask
from flask_sock import Sock
from config import Config
from data_access import flush_job_state, get_job_state

from tasks import allIsDone



app = Flask(__name__)
sock = Sock(app)
job_state = get_job_state()
if job_state and allIsDone(job_state['result_id']):
    flush_job_state()

app.config.from_object(Config)

from app import routes




    
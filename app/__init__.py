from flask import Flask
from flask_sock import Sock
from flask_moment import Moment
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from tasks import allIsDone
from data_access import flush_job_state, get_job_state
from sqlalchemy import MetaData


app = Flask(__name__)
sock = Sock(app)
moment = Moment(app)
job_state = get_job_state()
if job_state and allIsDone(job_state['result_id']):
    flush_job_state()

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

app.config.from_object(Config)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)

from app import routes, models





    
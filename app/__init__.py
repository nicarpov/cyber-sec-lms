from flask import Flask
from flask_sock import Sock
from config import Config


app = Flask(__name__)
sock = Sock(app)

app.config.from_object(Config)


from app import routes
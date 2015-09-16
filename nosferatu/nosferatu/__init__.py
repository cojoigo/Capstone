from flask import Flask
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from rq import Queue
from werkzeug.contrib.fixers import ProxyFix

from .assets import environment
from .worker import conn

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
db = SQLAlchemy(app)
q = Queue(connection=conn)

from .models import *
from .views import *

environment.init_app(app)
db_adaptor = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adaptor, app)

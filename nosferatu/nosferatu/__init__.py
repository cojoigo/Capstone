from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from werkzeug.contrib.fixers import ProxyFix

from .assets import environment


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)
if app.debug:
    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
db = SQLAlchemy(app)

schedule = BackgroundScheduler()

from .models import *
from .scheduler import schedule_rules
from .tasks import *
from .views import *

environment.init_app(app)
db_adaptor = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adaptor, app)
schedule_rules(schedule)
schedule.start()

from celery import Celery
from flask import Flask
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from werkzeug.contrib.fixers import ProxyFix

from .assets import environment

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            raise Exception("ASDF")
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
celery = make_celery(app)
db = SQLAlchemy(app)

@celery.task(bind=True)
def find_nodes_task(self):
    nodes = [
        {
            'id': 12341234,
            'ip': '1.2.3.4',
            'mac': 'A0:2B:03:C3:F3',
            'on': True,
        }, {
            'id': 12341235,
            'ip': '2.2.3.4',
            'mac': 'A0:2B:03:C3:F5',
            'on': False,
        }, {
            'id': 12341236,
            'ip': '3.2.3.4',
            'mac': 'A0:2B:03:C3:F4',
            'on': True,
        }
    ]
    return nodes

from .models import *
from .views import *

environment.init_app(app)
db_adaptor = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adaptor, app)

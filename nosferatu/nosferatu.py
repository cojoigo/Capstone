import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter

from assets import environment

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from base import *

environment.init_app(app)
db_adaptor = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adaptor, app)

if __name__ == '__main__':
    app.run()

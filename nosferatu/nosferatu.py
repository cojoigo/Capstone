import os
from flask import abort, Flask, redirect, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import (confirm_email_required, current_user, login_required,
                        UserManager, SQLAlchemyAdapter)
from flask_user.signals import user_sent_invitation, user_registered

from assets import environment

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import *

environment.init_app(app)

db_adaptor = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adaptor, app)


@user_registered.connect_via(app)
def after_registered_hook(sender, user, user_invite):
    print("USER REGISTERED")


@user_sent_invitation.connect_via(app)
def after_invitation_hook(sender, **kwargs):
    print("USER SENT INVITATION")


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

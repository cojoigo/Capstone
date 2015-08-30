from flask import render_template
from flask_user import login_required
from flask_user.signals import user_sent_invitation, user_registered

from nosferatu import app


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

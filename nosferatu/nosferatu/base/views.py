import logging
from flask import render_template, request, redirect, url_for, jsonify
from flask_user import login_required
from flask_user.signals import user_sent_invitation, user_registered
from rq.job import Job

from nosferatu import app, q, db
from worker import conn

from base.models import Node

log = logging.getLogger('debug')


@user_registered.connect_via(app)
def after_registered_hook(sender, user, user_invite):
    log.info('USER REGISTERED')


@user_sent_invitation.connect_via(app)
def after_invitation_hook(sender, **kwargs):
    log.info('USER SENT INVITATION')

def search_for_node():
    try:
        return "QWER"
        node = Node(
            name="Test",
            ip_addr='1.1.1.1',
            mac_addr='40:6c:8f:40:98:4d',
            user_id=3,
        )
        db.session.add(node)
        db.session.commit()
        print(node.id)
        return node.id
    except Exception as e:
        log.exception(e)
        return "ASDF"
        pass

@app.route('/registered_nodes/<job_key>', methods=['GET'])
def get_registered_node(job_key):
    print(job_key)
    job = Job.fetch(job_key, connection=conn)
    if job.is_finished:
        # node = Node.query.filter_by(id=job.result).first()
        # nodes = {
        #     'id': node.id,
        #     'ip': node.ip_addr,
        #     'mac': node.mac_addr,
        #     'userid': node.user_id,
        # }
        nodes = {
            'id': 12341234,
            'ip': '1.2.3.4',
            'mac': ':#:$:$:#:',
            'userid': 363456,
            'status': 'on',
        }
        return jsonify(nodes)
    else:
        return 'ERROR', 202

@app.route('/register_node', methods=['POST'])
def register_node():
    job = q.enqueue_call(func=search_for_node)
    log.info(job.get_id())
    print(job.get_id())
    return job.get_id()

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

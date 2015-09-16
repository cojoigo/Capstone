import logging

from flask import render_template, jsonify
from flask_user import login_required
from flask_user.signals import user_sent_invitation, user_registered

from . import app, cache, celery, db
from .models import Node

log = logging.getLogger('debug')


@user_registered.connect_via(app)
def after_registered_hook(sender, user, user_invite):
    log.info('USER REGISTERED')


@user_sent_invitation.connect_via(app)
def after_invitation_hook(sender, **kwargs):
    log.info('USER SENT INVITATION')


@celery.task(bind=True)
def search_for_node(self):
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


@app.route('/nodes/<node_id>', methods=['GET'])
@cache.memoize(timeout=5)
def get_node_status(node_id):
    pass


@app.route('/registered_nodes', methods=['GET'])
def registered_nodes():
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
    return jsonify(items=nodes)


@app.route('/registered_nodes/<job_id>', methods=['GET'])
def get_new_node(job_id):
    log.debug(job_id)
    job = search_for_node.AsyncResult(job_id)
    if job.ready():
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
            'on': True,
        }
        return jsonify(nodes)
    else:
        return 'ERROR', 202


@app.route('/register_node', methods=['POST'])
def register_node():
    job = search_for_node.apply_async()
    log.debug(job.id)
    return job.id


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

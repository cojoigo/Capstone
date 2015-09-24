import logging

from flask import render_template, jsonify
from flask_user import login_required
from flask_user.signals import user_sent_invitation, user_registered

from . import app, cache, celery, db
from .models import Node
from .tasks import *

log = logging.getLogger('debug')


@user_registered.connect_via(app)
def after_registered_hook(sender, user, user_invite):
    log.info('USER REGISTERED')


@user_sent_invitation.connect_via(app)
def after_invitation_hook(sender, **kwargs):
    log.info('USER SENT INVITATION')


@app.route('/nodes/<node_id>', methods=['GET'])
@cache.memoize(timeout=5)
@login_required
def get_node_status(node_id):
    pass

@app.route('/registered_nodes', methods=['GET'])
@login_required
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
@login_required
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
@login_required
def register_node():
    job = search_for_node.delay()
    log.debug(job.id)
    return job.id


@app.route('/find_nodes/<job_id>', methods=['GET'])
@login_required
def find_nodes(job_id):
    log.debug(job_id)
    job = find_nodes_task.AsyncResult(job_id)
    if job.ready():
        return jsonify(items=job.result)
    else:
        return 'ERROR', 202


@app.route('/find_nodes', methods=['POST'])
@login_required
def search_for_nodes():
    job = find_nodes_task.delay()
    log.debug(job.id)
    return job.id


@app.route('/nodes/<node_id>/test/start', methods=['GET'])
@login_required
def test_start(node_id):
    job = test_node_task.delay(node_id)
    return 'SUCCESS', 200


@app.route('/nodes/<node_id>/test/stop', methods=['GET'])
@login_required
def test_stop(node_id):
    job = test_node_task.delay(node_id, stop=True)
    return 'SUCCESS', 200


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

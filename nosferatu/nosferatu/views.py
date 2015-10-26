import logging

from flask import render_template, jsonify, request
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


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')


@app.route('/nodes/get/', methods=['GET'])
@login_required
def get_nodes():
    job = get_nodes_task.delay()
    return job.id


@app.route('/nodes/get/<job_id>', methods=['GET'])
@login_required
def nodes_jobs(job_id):
    print('get all the nodes', job_id)

    job = get_nodes_task.AsyncResult(job_id)
    if job.ready():
        print('  - all the gotten nodes', job_id, job.result)
        return jsonify(job.result)
    else:
        return 'Job is not ready', 202


@app.route('/nodes/add/', methods=['POST'])
@login_required
def add_node():
    print('Beginning add node', request.json)
    node = request.json
    job = add_node_task.delay(node)
    print(' - adding job', job.id)
    return job.id


@app.route('/nodes/add/<job_id>', methods=['GET'])
@login_required
def node_adding_jobs(job_id):
    print('adding single node', job_id)

    job = add_node_task.AsyncResult(job_id)
    job.state
    if job.ready():
        print('  - added node', job_id, job.result['id'])
        return jsonify(id=job.result['id'])
    else:
        return 'ERROR', 202


@app.route('/nodes/find/', methods=['GET'])
@login_required
def search_for_nodes():
    job = find_nodes_task.delay()

    print('find', job.id)
    return job.id


@app.route('/nodes/find/<job_id>', methods=['GET'])
@login_required
def find_nodes(job_id):
    print(job_id)

    job = find_nodes_task.AsyncResult(job_id)
    if job.ready():
        print('  find result', job.result)
        return jsonify(job.result)
    else:
        return 'ERROR', 202


# node = Node.query.filter_by(id=job.result).first()
# nodes = {
#     'id': node.id,
#     'ip': node.ip_addr,
#     'mac': node.mac_addr,
#     'userid': node.user_id,
# }


@app.route('/nodes/<node_id>', methods=['GET'])
@login_required
def get_node(node_id):
    print('Getting the node', node_id)
    job = get_node_task.delay(node_id)
    print(' - job id', job.id)
    return job.id


@app.route('/nodes/<node_id>/jobs/<job_id>', methods=['GET'])
@login_required
def node_jobs(node_id, job_id):
    print(' - Get Node Task', node_id, job_id)

    job = get_node_task.AsyncResult(job_id)
    print('   - job state', job.state)
    if job.ready():
        print('    - this singluar gotten node', job_id, job.result)
        return jsonify(job.result)
    else:
        return 'Job is not ready', 202


@app.route('/nodes/<node_id>/test/start', methods=['GET'])
@login_required
def test_start(node_id):
    test_node_task.delay(node_id)
    return 'SUCCESS', 200


@app.route('/nodes/<node_id>/test/stop', methods=['GET'])
@login_required
def test_stop(node_id):
    test_node_task.delay(node_id, stop=True)
    return 'SUCCESS', 200


@app.route('/nodes/<node_id>/rules', methods=['POST', 'GET'])
@login_required
def add_rule(node_id):
    if request.method == 'POST':
        print('Beginning add rule', node_id, request.json)
        rule = request.json
        job = add_rule_task.delay(node_id, rule)
        return job.id

    elif request.method == 'GET':
        print('Poll add rule', node_id, request.args)

        job_id = request.args.get('job_id')
        job = add_rule_task.AsyncResult(job_id)
        print('   - job state', job.state)
        if job.ready():
            print('    - this singluar gotten node', job_id, job.result['id'])
            return jsonify(job.result)
        else:
            return 'Job is not ready', 202


@app.route('/nodes/<node_id>/rules/all', methods=['POST', 'GET'])
@login_required
def get_all_rules(node_id):
    if request.method == 'POST':
        job = get_all_rules_task.delay(node_id)
        print('Beginning get all rules', node_id, job.id)
        return job.id

    elif request.method == 'GET':
        print('Poll get all rules', node_id, request.args)

        job_id = request.args.get('job_id')
        job = get_all_rules_task.AsyncResult(job_id)
        print('   - job state', job.state)
        if job.ready():
            print('    - this singluar gotten node', job_id, job.result)
            return jsonify(job.result)
        else:
            return 'Job is not ready', 202


@app.route('/nodes/<node_id>/rules/<rule_id>', methods=['POST', 'GET'])
@login_required
def get_single_rule(node_id, rule_id):
    if request.method == 'POST':
        print('Beginning add rule', node_id)
        job = add_rule_task.delay(node_id, rule_id)
        return job.id

    elif request.method == 'GET':
        print('Poll add rule', node_id, request.args)

        job_id = request.args['job_id']
        job = add_rule_task.AsyncResult(job_id)
        print('   - job state', job.state)
        if job.ready():
            print('    - this singluar gotten node', job_id, job.result['id'])
            return jsonify(job.result)
        else:
            return 'Job is not ready', 202

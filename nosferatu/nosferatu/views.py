import logging

from flask import render_template, jsonify, request
from flask_user import login_required, current_user
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
    job = add_node_task.delay(node, current_user.id)
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


@app.route('/nodes/<node_id>', methods=['GET', 'DELETE'])
@login_required
def get_node(node_id):
    if request.method == 'GET':
        print('Getting the node', node_id)
        job = get_node_task.delay(node_id)
        print(' - job id', job.id)
        return job.id
    elif request.method == 'DELETE':
        print('Deleting the node')
        return jsonify(delete_node_task(node_id))


@app.route('/nodes/<int:node_id>/jobs/<job_id>', methods=['GET'])
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


@app.route('/nodes/<node_id>/motion', methods=['POST'])
@login_required
def change_node_motion(node_id):
    change_motion_task(node_id, request.json)
    return 'SUCCESS', 200


@app.route('/nodes/<node_id>/toggle', methods=['POST'])
@login_required
def toggle_node(node_id):
    toggle_node_task(node_id)
    return 'SUCCESS', 200


@app.route('/nodes/<int:node_id>/status', methods=['GET'])
@login_required
def get_node_status(node_id):
    return jsonify(get_node_status_task(node_id))


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
            print('    - this added rule', job_id, job.result)
            return jsonify(job.result)
        else:
            return 'Job is not ready', 202


@app.route('/nodes/<int:node_id>/rules/all', methods=['POST', 'GET'])
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
            print('    - all the rules', job_id, job.result)
            return jsonify(job.result)
        else:
            return 'Job is not ready', 202


@app.route('/nodes/<int:node_id>/rules/<int:rule_id>', methods=['POST', 'GET', 'DELETE'])
@login_required
def get_single_rule(node_id, rule_id):
    if request.method == 'POST':
        print('Beginning add rule', node_id)
        job = get_rule_task.delay(node_id, rule_id)
        return job.id

    elif request.method == 'GET':
        print('Poll add rule', node_id, request.args)

        job_id = request.args['job_id']
        job = get_rule_task.AsyncResult(job_id)
        print('   - job state', job.state)
        if job.ready():
            print('    - this singluar gotten node', job_id, job.result)
            return jsonify(job.result)
        else:
            return 'Job is not ready', 202
    elif request.method == 'DELETE':
        print('Deleting rule', node_id, request.args)

        return jsonify(delete_rule_task(node_id, rule_id))

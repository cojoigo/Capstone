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


@app.route('/nodes/get', methods=['GET'])
@login_required
def get_nodes():
    return jsonify(get_nodes_task())


@app.route('/nodes/add', methods=['POST'])
@login_required
def add_node():
    print('Beginning add node', request.json)
    node = request.json
    result = add_node_task(node, current_user.id)
    return jsonify(id=result['id'])


@app.route('/nodes/find', methods=['POST'])
@login_required
def search_for_nodes():
    return jsonify(find_nodes_task())


@app.route('/nodes/<int:node_id>', methods=['GET', 'DELETE'])
@login_required
def get_node(node_id):
    if request.method == 'GET':
        print('Getting the node', node_id)
        return jsonify(get_node_task(node_id))
    elif request.method == 'DELETE':
        print('Deleting the node')
        return jsonify(delete_node_task(node_id))


@app.route('/nodes/test', methods=['POST'])
@login_required
def test_start():
    test_node_task(request.json)
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


@app.route('/nodes/<node_id>/rules', methods=['GET', 'POST'])
@login_required
def add_rule(node_id):
    if request.method == 'GET':
        print('Beginning get all rules', node_id)
        result = get_all_rules_task(node_id)
        print('    - all the rules', result)
        return jsonify(result)
    elif request.method == 'POST':
        print('Beginning add rule', node_id, request.json)
        rule = request.json
        return jsonify(add_rule_task(node_id, rule))


@app.route('/nodes/<int:node_id>/rules/<int:rule_id>', methods=['GET', 'DELETE'])
@login_required
def get_single_rule(node_id, rule_id):
    if request.method == 'GET':
        print('Beginning get rule', node_id)
        result = get_rule_task(node_id, rule_id)
        print('    - this singluar gotten node', result)
        return jsonify(result)

    elif request.method == 'DELETE':
        print('Deleting rule', node_id, request.args)
        return jsonify(delete_rule_task(node_id, rule_id))

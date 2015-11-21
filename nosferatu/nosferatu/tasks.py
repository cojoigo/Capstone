import logging

from . import cache, celery, db
from .models import Node, Rule
from .node_utils import (
    find_nodes, change_node_status, get_node_status,
    BadIpException, CommunicationException, BadStatusException,
)
from .task_lock import task_lock

log = logging.getLogger()


#######################################
# Rules Poll
#######################################
@celery.task
def rules_poll():
    rules = Rule.query.filter_by(type='Event')
    ids = []

    for rule in rules:
        ids.append(rule.event_node)

    nodes = Node.query.filter(Node.id.in_(ids)) if ids else []

    node_info = {}
    for node in nodes:
        node_info[node.id] = node

    for r in rules:
        node = node_info[r.eventNode]
        if node.status == r.event_node_state:
            ip_str = str(node.ip_addr)
            mac = str(node.mac_addr)

            if r.turn_on:
                action = 'ON'
            else:
                action = 'OFF'

            with task_lock(key=mac, timeout=10):
                status = change_node_status(ip_str, 'RELAY', action)

            led_status, motion_status, relay_status = status
            db_update_relay(node.id, relay_status)


#######################################
# Direct Node Communication
#######################################
def get_node_status_task(node_id):
    node = Node.query.filter_by(id=node_id).first()
    ip_str = str(node.ip_addr)
    mac = str(node.mac_addr)

    with task_lock(key=mac, timeout=10):
        try:
            status = get_node_status(ip_str)
        except (BadIpException, CommunicationException, BadStatusException) as e:
            print(e)
            status = ('Erroar', 'Erroar', 'Erroar')

    led_status, motion_status, relay_status = status
    db_update_relay(node_id, relay_status)

    return {
        'led': led_status,
        'relay': relay_status,
        'motion': motion_status,
    }


def test_node_task(args):
    if args['action'] == 'start':
        test = 'START'
    else:
        test = 'STOP'

    with task_lock(key=args['mac'], timeout=15):
        change_node_status(args['ip'], "TEST", test)


def find_nodes_task():
    # nodes = find_nodes()
    # '''
    nodes = {
        'a0:2b:03:c3:f3:12': {
            'ip': '1.2.3.4',
            'mac': 'a0:2b:03:c3:f3:12',
            'on': True,
        },
        'a0:2b:03:c3:f5:12': {
            'ip': '2.2.3.4',
            'mac': 'a0:2b:03:c3:f5:12',
            'on': False,
        },
        'a0:2b:03:c3:f4:12': {
            'ip': '3.2.3.4',
            'mac': 'a0:2b:03:c3:f4:12',
            'on': True,
        },
    }
    # '''
    return nodes


def toggle_node_task(node_id):
    node = Node.query.filter_by(id=node_id).first()

    ip_str = str(node.ip_addr)
    mac = str(node.mac_addr)

    with task_lock(key=mac, timeout=15):
        status = change_node_status(ip_str, "RELAY", "TOGGLE")

    db_update_relay(node_id, status)


def change_motion_task(node_id, status):
    node = Node.query.filter_by(id=node_id).first()

    ip_str = str(node.ip_addr)
    mac = str(node.mac_addr)

    status = status['motion'].upper()

    with task_lock(key=mac, timeout=15):
        status_reply = change_node_status(ip_str, "MOTION", status)

    # db_update_motion(node_id, status_reply)


#######################################
# Database calls
#######################################
def add_node_task(node, user_id):
    try:
        if not node['name']:
            raise Exception("Invalid Name")

        node = Node(
            name=node['name'],
            ip_addr=node['ip'],
            mac_addr=node['mac'],
            user_id=user_id,
        )
        db.session.add(node)
        db.session.commit()
        return {'id': node.id}
    except Exception as e:
        log.exception(e)


def get_nodes_task():
    nodes = Node.query.all()
    result = {}
    for i, node in enumerate(nodes):
        result['id{}'.format(i)] = node.id
    return result


def get_node_task(node_id):
    node = Node.query.get(node_id)
    return node.to_json()


def add_rule_task(node_id, rule):
    log.debug(rule)

    try:
        # Validate the zipcode
        zip_code = rule.get('zip_code')
        if zip_code is not None:
            for digit in zip_code:
                try:
                    int(digit)
                except ValueError:
                    zip_code = 0
            if not zip_code:
                zip_code = 0
                if rule.get('sched_type') == 'auto':
                    raise Exception("Error no Zipcode")

        rule = Rule(
            name=rule['name'],
            type=rule['type'],
            turn_on=rule['turn_on'],
            days='.'.join(rule['days']),

            sched_type=rule.get('sched_type'),
            sched_hour=rule.get('hour'),
            sched_minute=rule.get('minute'),
            sched_zip_code=zip_code,
            sched_time_of_day=rule.get('time_of_day'),

            event_node=rule.get('event_node'),
            event_node_status=rule.get('event_node_status'),

            node=node_id,
        )
        db.session.add(rule)
        db.session.commit()

        print(rule.id)

        return {'id': rule.id}
    except Exception as e:
        log.exception(e)


def delete_node_task(node_id):
    try:
        node = Node.query.get(node_id)
        db.session.delete(node)
        db.session.commit()
        return {'result': node.id}
    except:
        raise
    return {'result': False}


def get_all_rules_task(node_id):
    rules = Rule.query.filter_by(node=node_id).all()

    if rules:
        result = {}
        for i, rule in enumerate(rules):
            result['id{}'.format(i)] = rule.id
        return result
    return {}


def get_rule_task(node_id, rule_id):
    rule = Rule.query.filter_by(node=node_id, id=rule_id).first()
    if rule:
        if rule.type == 'Schedule':
            if rule.sched_type == 'manual':
                print(rule.sched_hour)
                info = 'at {}:{:02} {AMPM}'.format(
                    ((rule.sched_hour + 11) % 12) + 1,
                    rule.sched_minute,
                    AMPM='AM' if rule.sched_hour < 12 else 'PM'
                )
            else:
                info = rule.sched_time_of_day

        elif rule.type == 'Event':
            info = 'when `{node}` is {status}'.format(
                node=Node.query.get(rule.event_node).name,
                status='on' if rule.event_node_state else 'off'
            )
        else:
            info = rule.sched_type

        return {
            'id': rule.id,
            'name': rule.name,
            'turn_on': 'Turn ' + ('on' if bool(rule.turn_on) else 'off'),
            'days': [day.title() for day in rule.days.split('.')],
            'type': rule.type,
            'info': info,
        }


def delete_rule_task(node_id, rule_id):
    try:
        rule = Rule.query.filter_by(node=node_id, id=rule_id).first()
        if rule:
            db.session.delete(rule)
            db.session.commit()
            return {'result': rule.id}
    except:
        raise
    return {'result': False}


def db_update_status(node_id, status, status_type=None):
    if status_type is None:
        raise Exception("Status type can't be None")
    if status not in ['On', 'Off']:
        return

    status_map = {
        'On': True,
        'Off': False,
    }
    current_status = status_map[status]

    node = Node.query.get(node_id)
    setattr(node, status_type, current_status)
    db.session.commit()


def db_update_relay(node_id, status):
    db_update_status(node_id, status, status_type='relay_status')


def db_update_motion(node_id, status):
    db_update_status(node_id, status, status_type='motion_status')

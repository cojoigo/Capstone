import logging

from . import cache, celery, db
from .models import Node, Rule
from .node_utils import find_nodes, change_node_status, get_node_status
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

    nodes = Node.query.filter_by(id.in_(ids))
    for node in nodes:
        node_info[node.id] = (nodes.status, node.ip_addr, node.mac_addr)

    for r in rules:
        node = node_info[r.eventNode]
        if node[0] == r.event_node_state:
            ip_str = str(node[1])
            mac_str = str(node[2])

            if r.turn_on:
                with task_lock( key = mac, timeout = 15 ):
                    status = status_change( ip_str, "RELAY", "ON" )

            if !r.turn_on:
                with task_lock(key = mac, timeout = 15 ):
                    status = status_change( ip_str, "RELAY", "OFF")

#######################################
# Direct Node Communication
#######################################
def get_node_status_task(node_id):
    node = Node.query.filter_by(id=node_id).first()
    ip_str = str(node.ip_addr)
    mac = str(node.mac_addr)

    with task_lock(key=mac, timeout=15):
        try:
            status = get_node_status(ip_str).strip(' \t\r\n').split("&")
        except (BadIpException, CommunicationException, BadStatusException) as e:
            print(e.message)
            status = ('Erroar', 'Erroar', 'Erroar')

    led_status, motion_status, relay_status = status
    db_update_relay(node_id, relay_status)

    return {
        'led': led_status,
        'relay': relay_status,
        'motion': motion_status,
    }


@celery.task
def test_node_task(node_id, stop=False):
    if stop:
        test = 'ON'
    else:
        test = 'OFF'

    node = Node.query.filter_by(id=node_id).first()

    ip_str = str(node.ip_addr)
    mac = str(node.mac_addr)

    with task_lock(key=mac, timeout=15):
        change_node_status(ip_str, "TEST", test)

@celery.task(bind=True)
def find_nodes_task(self):
    nodes = find_nodes()

    '''
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
    '''

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
@celery.task(bind=True)
def add_node_task(self, node, user_id):
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


@celery.task(bind=True)
def get_nodes_task(self):
    nodes = Node.query.all()
    result = {}
    for i, node in enumerate(nodes):
        result['id{}'.format(i)] = node.id
    return result


@celery.task(bind=True)
def get_node_task(self, node_id):
    node = Node.query.get(node_id)
    return node.to_json()


@celery.task
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

        rule = Rule(
            name=rule['name'],
            type=rule['type'],
            turn_on=rule['turn_on'],
            days='.'.join(rule['days']),

            sched_type=rule.get('sched_type'),
            sched_hour=rule.get('hour'),
            sched_minute=rule.ge('minute'),
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
        raise


def delete_node_task(node_id):
    try:
        node = Node.query.get(node_id)
        db.session.delete(node)
        db.session.commit()
        return {'result': node.id}
    except:
        raise
    return {'result': False}


@celery.task
def get_all_rules_task(node_id):
    rules = Rule.query.filter_by(node=node_id).all()

    if rules:
        result = {}
        for i, rule in enumerate(rules):
            result['id{}'.format(i)] = rule.id
        return result
    return {}


@celery.task
def get_rule_task(node_id, rule_id):
    rule = Rule.query.filter_by(node=node_id, id=rule_id).first()
    if rule:
        return {
            'id': rule.id,
            'name': rule.name,
            'turn_on': str(bool(rule.turn_on)),
            'days': [day.title() for day in rule.days.split(',')],
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
    db_update_status(node_id, status, status_type='relay_status')

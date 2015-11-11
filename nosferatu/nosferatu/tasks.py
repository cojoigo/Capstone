import logging

from .node_lock import *
from . import cache, celery, db
from .models import Node, Rule
from .node_find import find_nodes
from .status_request import *
from .status_change import *
log = logging.getLogger()


#######################################
# Direct Node Communication
#######################################
def get_node_status_task(node_id):
    print("Wahho testing node", node_id)


    node = Node.query.filter_by(id=node_id).first()
    ip_str = str(node.ip_addr)
    mac = str( node.mac_addr )

    with task_lock( key = mac, timeout = 15 ):
        status = status_request( ip_str, "ALL" ).split("&")

    while len(status) < 3:
        status.append('5')
        # Error in status reply. Should be "status&status&status"

    for i in range(0, 3):
        db_update_status( node_id, i, status[i] )

    led_status = status[0]
    motion_status = status[1]
    relay_status = status[2]

    #Status will be a number:
    ## 0 == status OFF
    ## 1 == status ON
    ## 2 == Error establishing TCP connection to node
    ## 3 == Error sending status request packet
    ## 4 == Waiting for status reply timed out
    ## 5 == Received unknown status from node

    mapString = {
        'ON' : 'On',
        'OFF': 'Off',
        '0': 'Off',
        '1': 'On',
        '2': 'Erroar',
        '3': 'Erroar',
        '4': 'Erroar',
        '5': 'Erroar',
    }

    return {
        'led': mapString[led_status],
        'relay': mapString[relay_status],
        'motion': mapString[motion_status],
    }

    '''
    return {
        'led': 1,
        'relay': 0,
        'motion': 1,
    }
    '''

@celery.task
def test_node_task(node_id, stop=False):
    if stop:
        test = 'ON'
    else:
        test = 'OFF'

    node = Node.query.filter_by(id=node_id).first()

    ip_str = str(node.ip_addr)
    mac = str( node.mac_addr )

    with task_lock( key = mac, timeout = 15 ):
        status = status_change( ip_str, "TEST", test )


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
    mac = str( node.mac_addr )

    with task_lock( key = mac, timeout = 15 ):
        status = status_change( ip_str, "RELAY", "TOGGLE" )

    db_update_status( node_id, 3, status )


def change_motion_task(node_id, status):
    node = Node.query.filter_by(id=node_id).first()

    ip_str = str(node.ip_addr)
    mac = str(node.mac_addr)

    status = status['motion'].upper()

    with task_lock(key=mac, timeout = 15):
        status_reply = status_change(ip_str, "MOTION", status)

    db_update_status( node_id, 2, status_reply )

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
        zip_code = rule['zip_code']
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
            schedule_type=rule['schedule_type'],
            hour=rule['hour'],
            minute=rule['minute'],
            zip_code=zip_code,
            time_of_day=rule['time_of_day'],

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

def db_update_status( node_id, status_type, status ):
    if status_type == 0 or status_type == 1:
        return
        #TODO LED and Motion not yet implemented

    if status == "ON":
        current = True
    elif status == "OFF":
        current = False
    else:
        return

    node = Node.query.filter_by(id=node_id).first()
    node.relay_status = current
    db.session.commit()

    return



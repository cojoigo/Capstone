import logging

from . import cache, celery, db
from .models import Node, Rule#, DaysOfWeek, ScheduleTypes, TimeOfDay
from .node_find import find_nodes
from .status_request import *
from .status_change import *
import pprint
log = logging.getLogger()


@celery.task(bind=True)
def find_nodes_task(self):

    nodes = find_nodes()

    '''
    nodes = {
        'A0:2B:03:C3:F3': {
            'id': 12341234,
            'ip': '1.2.3.4',
            'mac': 'A0:2B:03:C3:F3',
            'on': True,
        },
        'A0:2B:03:C3:F5': {
            'id': 12341235,
            'ip': '2.2.3.4',
            'mac': 'A0:2B:03:C3:F5',
            'on': False,
        },
        'A0:2B:03:C3:F4': {
            'id': 12341236,
            'ip': '3.2.3.4',
            'mac': 'A0:2B:03:C3:F4',
            'on': True,
        },
    }
    '''

    return nodes


@celery.task(bind=True)
def get_node_task(self, node_id):

    if node_id == '1':
        node = {
            'id': 1,
            'ip': '192.168.1.32',
            'mac': 'A0:2B:03:C3:F3',
            'name': 'Bedroom',
            'on': True,
        }
        return node

    node = {
        'id': 12341238,
        'ip': '1.2.3.4',
        'mac': 'A0:2B:03:C3:F3',
        'name': 'Living room',
        'on': True,
    }
    return node


@celery.task(bind=True)
def get_nodes_task(self):
    nodes = {
        'id1': 1,
        'id2': 12341238,
    }
    return nodes


@celery.task(bind=True)
def add_node_task(self, req):
    return {'id': 12341234}
    try:
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


@celery.task
def test_node_task(node_id, stop=False):
    if stop:
        print('Stopping test')
    else:
        print('Starting test')


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


@celery.task
def get_all_rules_task(node_id):
    rules = Rule.query.filter_by(node=node_id).all()

    if rules:
        result = {}
        for i, rule in enumerate(rules):
            result['id{}'.format(i)] = rule.id
        return result


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


def get_node_status_task(node_id):

    # TODO Need to get Node's IP based on ID
    # TODO Also need which status to get: LED, RELAY, MOTION
    #status = status_request( ip, status_type )
    
    #Status will be a string: "ON", "OFF", or a number
    ## "1" == Error establishing TCP connection to node
    ## "2" == Error sending status request packet
    ## "3" == Waiting for status reply timed out

    print("Wahho testing node", node_id)
    return {
        'led': 1,
        'relay': 0,
        'motion': 1,
    }

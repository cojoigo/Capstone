import logging

from . import app, cache, celery, db
from .models import Node
from find_nodes import *
from subprocess import *
import pprint

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
    }'''

    return nodes

@celery.task(bind=True)
def get_node_task(self, node_id):
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
        'id1': 12341238,
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

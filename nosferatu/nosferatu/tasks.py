import logging

from . import app, cache, celery, db
from .models import Node


@celery.task(bind=True)
def find_nodes_task(self):
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
    return nodes


@celery.task(bind=True)
def add_node_task(self):
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


@celery.task
def test_node_task(node_id, stop=False):
    if stop:
        print('Stopping test')
    else:
        print('Starting test')

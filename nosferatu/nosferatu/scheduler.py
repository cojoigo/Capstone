from .models import *
from .node_utils import change_node_status
from .task_lock import task_lock


def change_state(affected_node, field, thing):
    # If field is `None` the action is "unchanged"
    if field is not None:
        # Otherwise it means on or off
        action = 'OFF'
        if field:
            action = 'ON'

        ip = str(affected_node.ip_addr)
        mac = str(affected_node.mac_addr)

        if thing == 'RELAY':
            if affected_node.relay_status != field:
                with task_lock(key=mac, timeout=10):
                    status = change_node_status(ip, thing, action)
                db_update_relay(affected_node.id, status)

        elif thing == 'MOTION':
            if affected_node.motion_status != field:
                with task_lock(key=mac, timeout=10):
                    status = change_node_status(ip, thing, action)
                db_update_motion(affected_node.id, status)



def rules_poll():
    rules = Rule.query.filter_by(type='Event')

    # Get all the nodes we could reference below
    ids = set()
    for rule in rules:
        ids.add(rule.node)
        ids.add(rule.event_node)

    # Map node id to node object
    node_info = {}
    nodes = Node.query.filter(Node.id.in_(ids)) if ids else []
    for node in nodes:
        node_info[node.id] = node

    # For each rule
    for rule in rules:
        affected_node = node_info[rule.node]
        node_to_check = node_info[rule.event_node]
        if affected_node and node_to_check:
            # If `node_to_check` has the state of `event_node_state` then `affected_node`
            # should change ITS state to the value of `turn_on`
            if node_to_check.relay_status == rule.event_node_state:
                change_state(affected_node, rule.turn_on, 'RELAY')
            if node_to_check.motion_status == rule.event_node_state:
                change_state(affected_node, rule.turn_motion_on, 'MOTION')

def change_node(mac, ip_str, action):
    with task_lock(key=mac, timeout=10):
        status = change_node_status(ip_str, 'RELAY', action)

def schedule_rules(scheduler):
    rules = Rule.query.filter_by(type='Schedule')
    ids = []
    print(len(list(rules)))

    for rule in rules:
        ids.append(rule.node)
    nodes = Node.query.filter(Node.id.in_(ids)) if ids else []
    node_info = {}

    for node in nodes:
        node_info[node.id] = node
    for rule in rules:
        node = node_info[rule.node]

        print(rule.sched_type)
        if rule.sched_type == 'manual':
            scheduler.add_job(change_state, 'cron',
                              day_of_week=','.join([d[:3] for d in rule.days.split('.')]),
                              hour=rule.sched_hour,
                              minute=rule.sched_minute,
                              args=[node, rule.turn_on, 'RELAY'],
                              id = str(rule.id)
                              )

    scheduler.add_job(rules_poll, 'interval',
                      seconds=1)
    scheduler.print_jobs()


def add_sched_rule(rule, scheduler):
    node = Node.query.get(rule.node)
    if rule.sched_type == 'manual':
        ip_str = str(node.ip_addr)
        mac = str(node.mac_addr)

        if rule.turn_on:
            action = 'ON'
        else:
            action = 'OFF'


        job = scheduler.add_job(change_node, 'cron',
                                day_of_week=','.join([d[:3] for d in rule.days.split('.')]),
                                hour=rule.sched_hour,
                                minute=rule.sched_minute,
                                args=[mac, ip_str, action],
                                id = str(rule.id))
        scheduler.print_jobs()


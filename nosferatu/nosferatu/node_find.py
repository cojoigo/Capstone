import subprocess
import pprint
from . import cache, celery, db
from .models import Node
from .node_auth import *
from .node_lock import *

def find_nodes():

    # Get list of IP/MAC pairs currently on network
    arp = subprocess.check_output("arp").decode()
    arp = arp.replace("\n", " ")
    arp_split = arp.split(" ")
    devices = []

    for ip in arp_split:
        if "192.168" in ip:
            arp1 = subprocess.check_output(["arp", ip]).decode()
            arp1 = arp1.replace("\n", " ")
            arp1_split = arp1.split(" ")
            for mac in arp1_split:
                if ":" in mac:
                    devices.append([ip, mac])

    db_nodes = Node.query.all()
    known_nodes = []
    unknown_nodes = []
    changed_nodes = []

    # Compare devices on network with nodes already in DB
    found = False
    for device in devices:
        found = False
        for db_node in db_nodes:
            if device[1] == db_node.mac_addr:
                # MAC match. Either known or changed IP
                found = True
                if device[0] == db_node.ip_addr:
                    known_nodes.append(device)
                else:
                    changed_nodes.append(device)
            continue

        # End of db_nodes reached, no matching MAC
        if found is False:
            unknown_nodes.append(device)

    # Authenticate and format nodes found on the network that are not in DB as a dict, to show to user
    formatted_unknown_nodes = {}

    for node in unknown_nodes:

        with task_lock( key = node[1], timeout = 15 ):
            status = node_auth( node[0] )

        if status.strip(' \t\r\n') == "N0$fEr@tU":
            formatted_unknown_nodes[ node[1] ] =  {'ip': node[0], 'mac': node[1]}


    print("\nFound and Auth'ed:")
    pprint.pprint(formatted_unknown_nodes)

    return formatted_unknown_nodes

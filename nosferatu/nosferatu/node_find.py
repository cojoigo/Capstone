import subprocess
import pprint 
from . import cache, celery, db
from .models import Node

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

    # TODO Used as example because VM does not have wifi network
    devices.append(["192.168.42.100", "9c:d9:17:62:65:62"])

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

    # TODO: Remove debug printing
    #print("known")
    #print(known_nodes)
    #print()
    #print("unknown")
    #print(unknown_nodes)
    #print()
    #print("changed")
    #print(changed_nodes)

    # TODO: What to do with nodes in Database that are no longer on the network?
    #       - Remove them from the DB
    #       - Keep them in the DB in case they were temporarily disconnected

    # Authenticate and format nodes found on the network that are not in DB as a dict, to show to user
    formatted_unknown_nodes = {}

    for node in unknown_nodes:
        status = node_auth( node[0] )
        if status.strip(' \t\r\n') == "N0$fEr@tU":
            formatted_unknown_nodes[ node[1] ] =  {'ip': node[0], 'mac': node[1]}

    print("\nFormatted")
    pprint.pprint(formatted_unknown_nodes)

    # Known MACs with different IPs -> update DB with new IPs
    # TODO: Add contents of changed_nodes to DB
    # Look in tasks.py for a DB write example
    
    return formatted_unknown_nodes

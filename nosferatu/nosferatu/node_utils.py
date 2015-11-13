import subprocess
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR

from .models import Node
from .task_lock import task_lock


DEFAULT_SEND_PORT = 12001


def node_auth(ip, send_port=DEFAULT_SEND_PORT):
    """Connect to a device through TCP and attempts to authenticate it.
    """

    sender = socket(AF_INET, SOCK_STREAM)
    addr = (ip, send_port)

    try:
        print("Trying to connect to auth " + ip)
        sender.connect(addr)
    except:
        print("Could not connect to auth " + ip)
        return "1"

    print("connected")

    try:
        print("sending auth to " + ip)
        sender.sendall(b'AUTH&HELLO.')
    except:
        print("Error sending auth req to " + ip)
        return "2"

    # If no status has been received within 3 seconds, assume connection is dead
    sender.settimeout(3)
    try:
        print("listening for auth from " + ip)
        status = sender.recv(1024).decode()
    except:
        print("Waiting for auth reply timed out from " + ip)
        return "3"

    return status


def find_nodes():
    """Find all nodes on the local network
    """
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

    # Authenticate and format nodes found on the network that
    # are not in DB as a dict, to show to user
    formatted_unknown_nodes = {}

    for node in unknown_nodes:
        with task_lock(key=node[1], timeout=15):
            status = node_auth(node[0])

        if status.strip(' \t\r\n') == "N0$fEr@tU":
            formatted_unknown_nodes[node[1]] = {'ip': node[0], 'mac': node[1]}

    print("\nFound and Auth'ed:")
    print(formatted_unknown_nodes)

    return formatted_unknown_nodes


def change_node_status(node_ip, request_type, status, send_port=DEFAULT_SEND_PORT):
    """Send a message to a specific node, to change its status.

    It can be used to change the state of the LED, Relay, or Motion Sensor.
    """

    if "192.168" in node_ip:
        pass
    else:
        print(node_ip + ": Invalid node for status change " + request_type)
        return 1

    addr = (node_ip, send_port)
    sender = socket(AF_INET, SOCK_STREAM)

    try:
        sender.connect(addr)
    except:
        print("Could not connect to {} to change status of {}".format(node_ip, request_type))
        return 3

    try:
        sender.send("{}&{}.".format(request_type, status).encode())
    except:
        print("Could not send message to {}".format(node_ip))
        return 4

    sender.settimeout(3)
    try:
        status = sender.recv(1024).decode()
    except:
        print("Waiting for message timed out on {}".format(node_ip))
        return 5

    sender.shutdown(SHUT_RDWR)
    sender.close()

    return status


def get_node_status(ip, status_type, send_port=DEFAULT_SEND_PORT):
    """Send a message to a known node to request a status.

    This can be used for the status of the node LED, relay, and motion sensor.
    """
    if "192.168" in ip:
        pass
    else:
        print("{}: Bad IP for status request {}".format(ip, status_type))
        return "2"

    sender = socket(AF_INET, SOCK_STREAM)
    addr = (ip, send_port)

    try:
        sender.connect(addr)
    except:
        print("Could not connect to {} for {} status request".format(ip, status_type))
        return "3"

    try:
        sender.sendall(("STATUS&{}.".format(status_type)).encode())
    except:
        print("Error sending status request to {}".format(ip))
        return "4"

    # If no status has been received within 3 seconds, assume connection is dead
    sender.settimeout(5)
    try:
        status = sender.recv(1024).decode()
    except:
        print("Waiting for status reply timed out on {}".format(ip))
        return "5"

    sender.shutdown(SHUT_RDWR)
    sender.close()

    if status_type == "ALL":
        return status

    if status == "OFF":
        return "0"
    elif status == "ON":
        return "1"
    else:
        return "5"

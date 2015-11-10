from socket import *
import sys
from datetime import *

# This script sends a message to a specific node, to change its status
# It can be used to change the state of the LED, Relay, or Motion Sensor


def change_status( node_ip, request_type, status, send_port = 12001 ):

    if "192.168" in node_ip:
        #print("Good node")
        pass
    else:
        print("invalid node for status change " + request_type)
        return 1

    addr = (node_ip, send_port)
    sender = socket(AF_INET, SOCK_STREAM)

    try:
        sender.connect(addr)
        #sendtime = datetime.now()
    except:
        print("Could not connect to change status of " + request_type)
        return 3

    try:
        sender.send( (request_type + "&" + status + ".").encode() )
    except:
        print("Could not send message")
        return 4


    sender.settimeout(3)
    try:
        status = sender.recv(1024).decode()
    except:
        print("Waiting for message timed out")
        return 5

    sender.shutdown( SHUT_RDWR )
    sender.close()

    #recvtime = datetime.now()

    #print("Roundtrip time " + str(recvtime-sendtime))

    #print(status)

    return status

from socket import *
from sys import *
from time import *
from datetime import *

# This script sets up a tcp connection to a known node, requests and waits for a status
# This can be used for the status of the node LED, relay, and motion sensor


def status_request(ip, status_type, send_port = 12001):

    if "192.168" in ip:
        #print("Good IP")
        pass
    else:
        print("Bad IP for status request " + status_type)
        return 2

    sender = socket(AF_INET, SOCK_STREAM)
    addr=(ip, send_port)

    try:
        print("Trying to connect for " + status_type + " status request")
        sender.connect(addr)
    except:
        print("Could not connect for " + status_type + " status request")
        return 3

    try:
        print("sending status request...")
        #first = datetime.now()
        sender.sendall( (status_type + "&STATUS.").encode() )
    except:
        print("Error sending status request")
        return 4


    # If no status has been received within 3 seconds, assume connection is dead
    sender.settimeout(3)
    try:
        print("listening for status...")
        status = sender.recv(1024).decode()
        #second = datetime.now()
    except:
        print("Waiting for status reply timed out")
        return 3

    sender.shutdown( SHUT_RDWR )
    sender.close()

    #print("heard \"" + status + "\"")
    #print( str(second-first) )

    if status == "OFF":
        return 0
    elif status == "ON":
        return 1
    else:
        return 5

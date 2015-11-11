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
        print(ip + ": Bad IP for status request " + status_type)
        return "2"

    sender = socket(AF_INET, SOCK_STREAM)
    addr=(ip, send_port)

    try:
        sender.connect(addr)
    except:
        print("Could not connect to " + ip + " for " + status_type + " status request")
        return "3"

    try:
        sender.sendall( ( "STATUS&" + status_type  + "." ).encode() )
    except:
        print("Error sending status request to " + ip)
        return "4"


    # If no status has been received within 3 seconds, assume connection is dead
    sender.settimeout(5)
    try:
        status = sender.recv(1024).decode()
        #second = datetime.now()
    except:
        print("Waiting for status reply timed out on " + ip)
        return "5"

    sender.shutdown( SHUT_RDWR )
    sender.close()

    if status_type == "ALL":
        return status

    if status == "OFF":
        return "0"
    elif status == "ON":
        return "1"
    else:
        return "5"

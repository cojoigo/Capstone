from socket import *
from sys import *
from time import *

# This script sets up a tcp connection to a known node, requests and waits for a status
# This can be used for the status of the node LED, relay, and motion sensor


def status_request(ip, status_type, send_port = 12001):

    if "192.168" in ip:
        print("Good IP")
    else:
        print("Bad IP")
        return "1"

    sender = socket(AF_INET, SOCK_STREAM)
    addr=(ip, send_port)

    try:
        print("Trying to connect for " + status_type + " status request")
        sender.connect(addr)
    except:
        print("Could not connect for " + status_type + " status request")
        return "1"
        
    try:
        print("sending status request...")
        sender.sendall( (status_type + "&STATUS.").encode() )
    except:
        print("Error sending status request")
        return "2"
            
    
    # If no status has been received within 3 seconds, assume connection is dead
    sender.settimeout(3)
    try:
        print("listening for status...")
        status = sender.recv(1024).decode()
    except:
        print("Waiting for status reply timed out")
        return "3"
        
    print("heard \"" + status + "\"")
    return status    

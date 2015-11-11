#!/usr/bin/python3

# This script sets up a tcp connection to a device and attempts to authenticate it

from socket import *
from sys import *
from time import *


def node_auth(ip, send_port = 12001):

    sender = socket(AF_INET, SOCK_STREAM)

    addr=(ip, send_port)

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

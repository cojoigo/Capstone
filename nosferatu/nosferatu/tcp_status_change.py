#!/usr/bin/python3

# This script sends a message to a specific node, to change its state. 
# The node and the desired state are passed in. 

from socket import *
import sys
from datetime import *

if len(sys.argv) != 3:
	print("Must pass node and status")
	exit()

if "192.168" in sys.argv[1]:
	node=sys.argv[1]
	print("Good node")
else:
	print("invalid node")
	exit()

if sys.argv[2] == "ON" or sys.argv[2] == "OFF":
	new_status=sys.argv[2].encode()
	print("Good status")
else:
	print("Invalid status")
	exit()

#Non status request messages should go over port 12001
send_port = 12001
addr = (node, send_port)

sender = socket(AF_INET, SOCK_STREAM)

#TODO put this in try except
sender.connect(addr)

sendtime = datetime.now()

#TODO put this in try except
sender.send(b"setstatus&"+new_status)

sender.settimeout(3)

status = sender.recv(1024).decode()
recvtime = datetime.now()

print("difference " + str(recvtime-sendtime))

print(status)

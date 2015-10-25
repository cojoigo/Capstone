#!/usr/bin/python3
from socket import *
from datetime import *
from sys import *
from time import *
from status_request_tcp import *


#The functionality of this script will be replaced by Javascript calls from the UI


nodes=[]

#TODO this will be replaced by a DB call within the while
nodes.append(["192.168.42.12", "MA:CA:DD:RE:SS:00"])

while True:
	#TODO Get list of nodes from DB
	for node in nodes:

		#TODO Should each monitor_status call be done in a separate thread?
		status = monitor_status(node[0])
		#TODO Do something with status

		if type(status) != type(str()):
			status=str(status)

		print("status: \"" + status + "\"")
	sleep(1)


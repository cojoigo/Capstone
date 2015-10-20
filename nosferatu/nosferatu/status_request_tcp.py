#!/usr/bin/python3

# This script sets up a tcp connection to a known node, requests and waits for a status

from socket import *
from sys import *
from time import *


def monitor_status(ip, send_port = 12001):

	sender = socket(AF_INET, SOCK_STREAM)

	addr=(ip, send_port)

	# TODO: Need a blocking exceptionless way to connect. 
	# server must initiate connection to node to ensure that there is 
	# exactly 1 status socket per node
	# If node is not waiting for a connection request, exception will be thrown
	try:
		print("Trying to connect")
		sender.connect(addr)
	except:
		print("Could not connect")
		return 1
		
	print("connected")
	
	try:
		print("sending...")
		sender.sendall(b'statusrequest')
	except:
		print("Error sending message")
		return 2
			
	
	# If no status has been received within 3 seconds, assume connection is dead
	sender.settimeout(3)
	try:
		print("listening...")
		status = sender.recv(1024).decode()
	except:
		print("Waiting for status reply timed out")
		return 3
		
	print("heard \"" + status + "\"")
	return status	

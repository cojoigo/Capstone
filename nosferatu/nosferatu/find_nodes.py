#!/usr/bin/python3

# This script calls arp to find new possible nodes on the network


# This script is called from tasks.py 

import pprint
from subprocess import *

def find_nodes():
	# Get list of IP/MAC pairs currently on network
	arp=check_output("arp").decode()
	arp=arp.replace("\n", " ")
	arp_split=arp.split(" ")
	devices=[]

	for ip in arp_split:
		if "192.168" in ip:
			arp1 = check_output(["arp", ip]).decode()
			arp1 = arp1.replace("\n", " ")
			arp1_split = arp1.split(" ")
			for mac in arp1_split:
				if ":" in mac:
					devices.append([ip, mac])

	# TODO: Query DB for known IP/MAC
	#Look in views.py for example DB request call
	db_nodes=[]
	known_nodes=[]
	unknown_nodes=[]
	changed_nodes=[]

	##Used as example. Need real DB call here to populate db_nodes
	db_nodes.append(["192.168.42.10", "9c:d9:17:62:65:62"])

	# Compare devices on network with nodes already in DB
	found=False
	for device in devices:
		found=False
		for db_node in db_nodes:
			if device[1] == db_node[1]:
				# MAC match. Either known or changed IP
				found=True
				if device[0] == db_node[0]:
					known_nodes.append(device)
				else:
					changed_nodes.append(device)
			continue
	
		# End of db_nodes reached, no matching MAC
		if found == False:
			unknown_nodes.append(device)
	
	# TODO: Remove debug printing
	print("known")
	print(known_nodes)
	print()
	print("unknown")
	print(unknown_nodes)
	print()
	print("changed")
	print(changed_nodes)
	
	# TODO: What to do with nodes in Database that are no longer on the network?
	#       - Remove them from the DB
	#       - Keep them in the DB in case they were temporarily disconnected
	
	####### TODO: Need to authenticate unknown_nodes before presenting them to the user
	
	# Unknown devices-> return dictionary (same style as in tasks.py)
	formatted_unknown_nodes=[]
	for node in unknown_nodes:
		formatted_unknown_nodes.append( { 'ip':node[0], 'mac':node[1] } )
	
	#print("\nFormatted")
	#pprint.pprint(formatted_unknown_nodes)
	
	
	# Known MACs with different IPs -> update DB with new IPs
	# TODO: Add contents of changed_nodes to DB
	# Look in tasks.py for a DB write example
	return formatted_known_nodes

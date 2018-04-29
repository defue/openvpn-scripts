#!/usr/bin/env python3

import re
import ipaddress
from anytree import Node, RenderTree

max_routes = 8192

ignored = [
	'127.0.0.1',
	'0.0.0.',
	'178.248.233.33',
	'82.192.95.170',
	'192.168.0',
	'192.168.1',
	'192.168.2',
	'192.168.44',
	'192.168.88',
	'192.168.100',
	'1.1.1.1',
	'1.2.3.4',
	'172.16.0.',
	'10.0.0.'
]


def ips_count_in_subnet(subnet):
    i = 32 - subnet.prefixlen
    return max(pow(2, i) - 2, 1)


with open('list.xml') as file:
	listxml = file.read()

ips = []

# find all ips with subnet if present
for ip in re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(?:/[0-9]+)?', listxml):
	ignore = False
	for ignoreip in ignored:
		if ip.startswith(ignoreip):
			print('ignore %s' % ip)
			ignore = True
	if not ignore:
		ips.append(ip)

print('IPs read: %d' % len(ips))

# deduplicate
ips = list(set(ips))
print('IPs deduplicated: %d' % len(ips))


# calc amount of blocked ips
blocked = 0
for ip in ips:
	blocked += ips_count_in_subnet(ipaddress.IPv4Network(ip))

print('Total blocked ips: %d  or %g%% of overall ip4 amount' % (blocked, round(blocked * 100 / ips_count_in_subnet(ipaddress.IPv4Network('0.0.0.0/0')), 1)))


nodes = []
#subnets = []
for ip in ips:
	net = ipaddress.IPv4Network(ip)
	net.__setattr__('is_from_ips_list', True) # set custom attribute
	nodes.append(Node(net))
	# if net.prefixlen != 32:
	# 	subnets.append(net)

# remove ips that belongs to subnets
# for net in nodes:

print()
print('Generating network tree')
for i in reversed(range(32)):
	parent_nodes = {} # use dictionary for better efficiency
	for node in nodes:
		# merge node and its child if there is only 1 child, don't merge nodes taken from the ip list
		if not node.name.is_from_ips_list and len(node.children) == 1:
			node = node.children[0]
		# remove children for nodes from the list
		if node.name.is_from_ips_list:
			node.children = []
		net = node.name
		if net.prefixlen > i:
			# search for a suitable parent node in parent_nodes
			parent_net = net.supernet(new_prefix=i)
			parent_node = parent_nodes.get(parent_net.with_prefixlen)
			if parent_node:
				node.parent = parent_node
			else:
				# not found
				parent_net.__setattr__('is_from_ips_list', False)
				parent_node = Node(parent_net)
				node.parent = parent_node
				parent_nodes[parent_net.with_prefixlen] = parent_node
		else:
			# skip searching for a parent node for higher order subnets
			parent_nodes[node.name.with_prefixlen] = node
	nodes = list(parent_nodes.values())
	print(' - subnet prefix %d nodes: %d' % (i, len(nodes)))

# print tree
# for pre, fill, node in RenderTree(nodes[0]): print("%s%s" % (pre, node.name))

print()
print('Calculating routes...')
# expand tree until max_routes is reached
while len(nodes) < max_routes:
	index, node = min(enumerate(nodes), key=lambda e: e[1].name.prefixlen if len(e[1].children) > 0 else 32)
	if len(node.children) == 0:
		break
	del nodes[index] # remove node from nodes
	nodes += list(node.children) # add its children

# print final result
print('Making routes.txt...')
routed_ips_amount = 0
with open('routes.txt', 'w') as file:
	file.truncate()
	for node in nodes:
		# file.write(node.name.with_prefixlen)
		# print(node.name.with_prefixlen, file=file)
		print('push "route %s"' % node.name.with_netmask.replace('/', ' '), file=file)
		routed_ips_amount += ips_count_in_subnet(node.name)

print()
print('Total routes: %d' % len(nodes))
print('Total routed ips %d or %g%% of overall ip4 amount' % (routed_ips_amount, round(routed_ips_amount * 100 / ips_count_in_subnet(ipaddress.IPv4Network('0.0.0.0/0')), 1)))

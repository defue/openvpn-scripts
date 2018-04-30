#!/usr/bin/env python3

import ipaddress
from anytree import Node, RenderTree

def build_network_tree(ips, verbose=False):
	if verbose:
		print()
		print('Generating network tree...')
	
	nodes = []
	for ip in ips:
		net = ipaddress.IPv4Network(ip)
		net.__setattr__('is_from_ips_list', True) # set custom attribute
		nodes.append(Node(net))
	
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
		if verbose:
			print(' - subnet prefix %d nodes: %d' % (i, len(nodes)))
	return nodes[0]

def print_network_tree(parent_node):
	for pre, fill, node in RenderTree(parent_node): print("%s%s" % (pre, node.name))


if __name__ == "__main__":
	from custom_ips import ips as custom_ips
	parent_node = build_network_tree(custom_ips)
	print_network_tree(parent_node)
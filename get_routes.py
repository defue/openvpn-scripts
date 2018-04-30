#!/usr/bin/env python3

import re
import ipaddress

from custom_ips import ips as custom_ips

def ips_count_in_subnet(subnet):
	i = 32 - subnet.prefixlen
	return max(pow(2, i) - 2, 1)

with open('list.xml') as file:
	listxml = file.read()

ips = []
# find all ip subnets
for ip in re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}', listxml):
	ips.append(ip)

# add custom ips
ips += custom_ips

print('IPs read: %d' % len(ips))

# deduplicate
ips = list(set(ips))
print('IPs deduplicated: %d' % len(ips))

routed_ips_amount = 0
with open('routes.txt', 'w') as file:
	file.truncate()
	for ip in ips:
		# file.write(node.name.with_prefixlen)
		# print(node.name.with_prefixlen, file=file)
		net = ipaddress.IPv4Network(ip)
		print('push "route %s"' % net.with_netmask.replace('/', ' '), file=file)
		routed_ips_amount += ips_count_in_subnet(net)

print()
print('Total routes: %d' % len(ips))
print('Total routed ips %d or %g%% of overall ip4 amount' % (routed_ips_amount, round(routed_ips_amount * 100 / ips_count_in_subnet(ipaddress.IPv4Network('0.0.0.0/0')), 1)))

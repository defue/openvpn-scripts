#!/usr/bin/env python3

import re
import ipaddress

def ips_count_in_subnet(subnet):
	i = 32 - subnet.prefixlen
	return max(pow(2, i) - 2, 1)

with open('list.xml') as file:
	listxml = file.read()

ips = []
# find all ip subnets
for ip in re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}', listxml):
	ips.append(ip)

print('IPs read: %d' % len(ips))

# add manual ips
ips += [
	# linkedin.com
	'185.63.144.0/24',
	'185.63.145.0/24',
	'108.174.10.10/32',
	'108.174.11.0/24',
	'108.174.5.0/24',
	'91.225.248.0/24',
	# rutracker.org and bt3.t-ru.org trackers
	'195.82.146.0/24',
	# telegram
	'149.154.167.0/24',
	'149.154.174.0/24',
]

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

#!/bin/sh

# Download list
curl --compress -o list_cp1251.xml https://raw.githubusercontent.com/zapret-info/z-i/master/dump.csv
iconv -f cp1251 -t utf8 list_cp1251.xml > list.xml

# Get IP addresses from list
./getips.py

# deploy routes to openvpn
cp routes.txt /etc/openvpn/ccd/DEFAULT

### Scripts for creating routes for openvpn server

install and setup openvpn, all settings by default
```
https://github.com/Nyr/openvpn-install
```

create routes dir
```
mkdir /etc/openvpn/ccd
```

add the below line to /etc/openvpn/server.conf
```
client-config-dir /etc/openvpn/ccd
```

comment the below line in the config
```
push "redirect-gateway def1 bypass-dhcp"
```

comment all 'push "dhcp-option DNS' lines and add google DNS with routes
```
# Google public DNS - main
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"
push "route 8.8.8.8 255.255.255.255"
push "route 8.8.4.4 255.255.255.255"

# Yandex family DNS - optional
push "route 77.88.8.7 255.255.255.255"
push "route 77.88.8.3 255.255.255.255"
```

restart openvpn
```
systemctl restart openvpn@server.service
```

dependancies for scripts
```
locale-gen ru_RU.UTF-8
apt install python3-pip
pip3 install anytree
```

then clone the repository and run doall.sh

add to cron, no need to reload openvpn as routes are updated automatically
```
crontab -e
00 6 * * *  /home/openvpn-scripts/doall.sh # run the script at 6 a.m. everyday
```

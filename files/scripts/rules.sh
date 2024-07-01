#!/bin/bash
echo "Clearing rules..."
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -t filter -F
echo "Setting NAT..."
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -d 172.16.5.0/24 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
echo "Writing rules..."
iptables -A FORWARD -s 172.16.5.9 -d 127.0.0.0/8 -j ACCEPT
iptables -A FORWARD -s 172.16.5.9 -d 10.0.0.0/8 -j ACCEPT
iptables -A FORWARD -s 172.16.5.9 -d 172.16.0.0/16 -j ACCEPT
iptables -A FORWARD -s 172.16.5.9 -d 192.168.0.0/16 -j ACCEPT
iptables -A FORWARD -s 172.16.5.9 -d 8.8.8.8 -j ACCEPT
iptables -A FORWARD -s 172.16.5.9 -d 8.8.4.4 -j ACCEPT
iptables -A FORWARD -s 172.16.5.9 -d 91.218.140.112 -j ACCEPT
iptables -A FORWARD -s 172.16.5.9 -j DROP
iptables-save > /etc/iptables/rules.v4
echo "RULES saved to /etc/iptables/rules.v4"

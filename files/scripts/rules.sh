#/bin/bash
echo "Clearing rules..."
iptables -F
echo "Writing rules..."
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -A OUTPUT -d 127.0.0.0/8 -j ACCEPT
iptables -t nat -A OUTPUT -d 10.0.0.0/8 -j ACCEPT
iptables -t nat -A OUTPUT -d 172.16.0.0/16 -j ACCEPT
iptables -t nat -A OUTPUT -d 192.168.0.0/16 -j ACCEPT
iptables -t nat -A OUTPUT -d 8.8.8.8 -j ACCEPT
iptables -t nat -A OUTPUT -d 8.8.4.4 -j ACCEPT
iptables -t nat -A OUTPUT -d 91.218.140.112 -j ACCEPT
iptables -t nat -A OUTPUT -j DROP
iptables-save > /etc/iptables/rules.v4
echo "Saved rules to /etc/iptables/rules.v4"

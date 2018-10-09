import csv
import ipaddress
import sys
import os
import urllib.request
import io

netbox = 'https://netbox.minserver.dk/ipam/prefixes/?q=&within_include=&family=&mask_length=&vrf=npflan&status=1&role=server-net-dhcp&export'
data = urllib.request.urlopen(netbox).read()

datafile = os.path.join(os.path.dirname(__file__), 'data.csv')
with open(datafile, 'wb+') as f:
    f.write(data)

reader = csv.DictReader(io.StringIO(data.decode()), delimiter=',', quotechar='|')

print('default-lease-time 7200;\n')
print('max-lease-time 28800;\n')
print('authoritative;\n')

print('allow booting;\n')

print('option domain-name "server.npf";\n')
print('option domain-name-servers 10.101.128.128;\n')


print('ddns-updates on;\n')
print('ddns-update-style interim;\n')

print('''
zone rack1.server.npf. {
  primary 10.101.128.128;
}
zone rack2.server.npf. {
  primary 10.101.128.128;
}
zone rack3.server.npf. {
  primary 10.101.128.128;
}
zone 101.100.10.in-addr.arpa. {
  primary 10.101.128.128;
}
zone 102.100.10.in-addr.arpa. {
  primary 10.101.128.128;
}
zone 103.100.10.in-addr.arpa. {
  primary 10.101.128.128;
}
''')
print('subnet 10.101.1.0 netmask 255.255.255.0 {}')
print('subnet 10.101.2.0 netmask 255.255.255.0 {}')
print('subnet 10.101.3.0 netmask 255.255.255.0 {}')
print('subnet 10.101.4.0 netmask 255.255.255.0 {}')
print('subnet 10.101.5.0 netmask 255.255.255.0 {}')
print('subnet 10.101.6.0 netmask 255.255.255.0 {}')
print('subnet 10.101.7.0 netmask 255.255.255.0 {}')
print('subnet 10.101.8.0 netmask 255.255.255.0 {}')
print('subnet 10.101.9.0 netmask 255.255.255.0 {}')
print('subnet 10.100.128.0 netmask 255.255.192.0 {}')


for row in reader:
    print("# " + ' - '.join((n for n in (row['role'], row['description']) if n)))
    try:
        ip = ipaddress.IPv4Network(row['prefix'])
    except ipaddress.AddressValueError:
        print(row['prefix'] + " is not a valid ip",file=sys.stderr)
    parts = ip.with_netmask.split('/')
    network = parts[0]
    subnetmask = parts[1]
    print("subnet " + network + " netmask " + subnetmask + " {")
    print("\t pool {")
    print("\t\t range " + str(ip[150]) + " " + str(ip[pow(2, (32-ip.prefixlen))-50]) + ";")
    print("\t\t option routers " + str(ip[1]) + ";")
    print('\t\t option domain-name "'+row['description']+'";\n')
    print('\t\t next-server 10.100.101.223;\n')
    print('\t\t filename "pxelinux.0";\n')
    print('\t\t include "/dhcp/config/reservation.ip.'+network+'.conf";\n')
    print("\t}")
    print("}\n")
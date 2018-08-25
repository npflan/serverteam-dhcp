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

reader = csv.reader(io.StringIO(data.decode()), delimiter=',', quotechar='|')

print('default-lease-time 7200;')
print('max-lease-time 28800;\n')
print('authoritative;\n')
print('option domain-name "server.npf";\n')
print('option domain-name-servers 10.96.5.1;\n')

print('omapi-port 7911;')
print('omapi-key omapi_key;\n')

print('key omapi_key {')
print('\t algorithm hmac-md5;')
print('\t secret LsMkrX1xprEQQBoeGAC6NvokcA/mcuD5LnBqD/2gxJEpZqTTRN7vtPm0BVW03zl0oo1qWCVrNTqsoAq2B8hrsg==;')
print('};\n')


for row in reader:
    if row[7].lower() == "Access".lower() or row[7].lower() == "Wireless".lower() or row[9].lower() == "AP-MGMT".lower():
        if row[9].lower() == 'Wireless Networks'.lower():
            continue;
        print("# " + ' - '.join((n for n in (row[7], row[9]) if n)))
        ip = ipaddress.IPv4Network(row[0])
        parts = ip.with_netmask.split('/')
        network = parts[0]
        subnetmask = parts[1]
        print("subnet " + network + " netmask " + subnetmask + " {")
        print("\t pool {")
        print("\t\t range " + str(ip[4]) + " " + str(ip[pow(2, (32-ip.prefixlen))-6]) + ";")
        print("\t\t option routers " + str(ip[1]) + ";")
        print("\t}")
        print("}\n")
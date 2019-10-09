import csv
import ipaddress
import sys
import os
import urllib.request
import io
import json

subnet4 = []

netbox = 'https://netbox.minserver.dk/ipam/prefixes/?q=&within_include=&family=&mask_length=&vrf=npflan&status=1&role=server-net-dhcp&export'
data = urllib.request.urlopen(netbox).read()

netbox2 = 'https://netbox.minserver.dk/ipam/prefixes/?q=&within_include=&family=&mask_length=&vrf=npflan&status=1&role=management-server&export'
data2 = urllib.request.urlopen(netbox2).read()


datafile = os.path.join(os.path.dirname(__file__), 'data.csv')
with open(datafile, 'wb+') as f:
    f.write(data)
    f.write(data2)

reader = csv.DictReader(io.StringIO(data.decode()),
                        delimiter=',', quotechar='|')
reader2 = csv.DictReader(io.StringIO(data2.decode()),
                         delimiter=',', quotechar='|')

for row in reader:
    try:
        ip = ipaddress.IPv4Network(row['prefix'])
    except ipaddress.AddressValueError:
        print(row['prefix'] + " is not a valid ip", file=sys.stderr)
    parts = ip.with_netmask.split('/')
    network = parts[0]
    subnetmask = parts[1]

    subnet = {
        "subnet": network+"/"+str(ip.prefixlen),
        "pools": [
            {
                "pool": str(ip[150])+"-"+str(ip[pow(2, (32-ip.prefixlen))-56])
            }
        ],
        "option-data": [
            {
                "name": "routers",
                "data": str(ip[1])
            },
            {
                "name": "boot-file-name",
                "data": "pxelinux.0"
            },
            {
                "name": "domain-name",
                "data": row['description']
            },
            {
                "name": "tftp-server-name",
                "data": "10.100.101.223"
            }
        ]
    }

    reservations_file = './reservation.ip.'+network+'.json'
    if os.path.isfile(reservations_file):
        with open(reservations_file,encoding='utf-8') as json_data:
            reservations = json.load(json_data)
            subnet["reservations"] = reservations["reservations"]

    subnet4.append(subnet)

for row in reader2:
    try:
        ip = ipaddress.IPv4Network(row['prefix'])
    except ipaddress.AddressValueError:
        print(row['prefix'] + " is not a valid ip", file=sys.stderr)
    parts = ip.with_netmask.split('/')
    network = parts[0]
    subnetmask = parts[1]




    subnet = {
        "subnet": network+"/"+str(ip.prefixlen),
        "pools": [
            {
                "pool": str(ip[150])+"-"+str(ip[pow(2, (32-ip.prefixlen))-56])
            }
        ],
        "option-data": [
            {
                "name": "routers",
                "data": str(ip[1])
            },
            {
                "name": "boot-file-name",
                "data": "pxelinux.0"
            },
            {
                "name": "domain-name",
                "data": row['description']
            }
        ]
    }

    reservations_file = './reservation.ip.'+network+'.json'
    if os.path.isfile(reservations_file):
        with open(reservations_file,encoding='utf-8') as json_data:
            reservations = json.load(json_data)
            subnet["reservations"] = reservations["reservations"]

    subnet4.append(subnet)

keaconfig = {
    "Dhcp4": {
        "dhcp-ddns": {
             "enable-updates": True,
             "qualifying-suffix": "server.npf"
        },
        "interfaces-config": {
            "interfaces": [ "*" ]
        },
        "valid-lifetime": 4000,
        "renew-timer": 1000,
        "rebind-timer": 2000,
        "subnet4": subnet4,
        "lease-database": {
            "type": "memfile",
            "name": "leases4"
        },
        "control-socket":
        {
            "socket-type": "unix",
            "socket-name": "/kea/socket/socket-v4"
        }
    },
    "DhcpDdns":
    {
        "ip-address": "127.0.0.1",
        "port": 53001,
        "dns-server-timeout": 1000,

        "user-context": {"version": 1},

        "control-socket":
        {
            "socket-type": "unix",
            "socket-name": "/kea/socket/socket-d2"
        },

        "forward-ddns":
        {
            "ddns-domains":
            [
                {
                    "name": "rack1.server.npf.",
                    "dns-servers":
                    [
                        {
                            "ip-address": "10.101.128.128"
                        }
                    ]
                },
                {
                    "name": "rack2.server.npf.",
                    "dns-servers":
                    [
                        {
                            "ip-address": "10.101.128.128"
                        }
                    ]
                },
                {
                    "name": "rack3.server.npf.",
                    "dns-servers":
                    [
                        {
                            "ip-address": "10.101.128.128"
                        }
                    ]
                }
            ]
        },
        "reverse-ddns":
        {
            "ddns-domains":
            [
                {
                    "name": "101.100.10.in-addr.arpa.",
                    "dns-servers":
                    [
                        {
                            "ip-address": "127.0.0.1",
                            "port": 53001
                        },
                        {
                            "ip-address": "10.101.128.10"
                        }
                    ]
                },
                {
                    "name": "102.100.10.in-addr.arpa.",
                    "dns-servers":
                    [
                        {
                            "ip-address": "127.0.0.1",
                            "port": 53001
                        },
                        {
                            "ip-address": "10.101.128.10"
                        }
                    ]
                },
                {
                    "name": "103.100.10.in-addr.arpa.",
                    "dns-servers":
                    [
                        {
                            "ip-address": "127.0.0.1",
                            "port": 53001
                        },
                        {
                            "ip-address": "10.101.128.10"
                        }
                    ]
                }
            ]
        }
    }
}

print(json.dumps(keaconfig, sort_keys=True, indent=4, separators=(',', ': ')))

import csv
import sys
import os
import urllib.request
import io
import json
import re

reservation_file = 'reservation.ip.10.100.103.0.conf'

datafile = os.path.join(os.path.dirname(__file__), reservation_file)
with open(datafile, 'r') as myfile:
  data = myfile.read()

test = re.findall(r"host ([ip1234567890-]+).*\n.*hardware ethernet ([^;]+);.*\n.*fixed-address ([^;]+);", data, re.MULTILINE)

export = {}
export["reservations"] = []

for ipStr in test:
    export["reservations"].append({
        "hostname": ipStr[0],
        "ip-address": ipStr[2],
        "hw-address": ipStr[1]
    })

print(json.dumps(export, sort_keys=True, indent=4, separators=(',', ': ')))

datafile = os.path.join(os.path.dirname(__file__), reservation_file)
with open(datafile, 'w') as f:
    json.dump(export, f, sort_keys=True, indent=4, separators=(',', ': '))
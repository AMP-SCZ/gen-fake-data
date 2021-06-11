#!/usr/bin/env python

from config import config
import requests
import sys

if len(sys.argv)!=2 or sys.argv[1] in ['-h','--help']:
    print('''Usage: /path/to/import_records.py fake_out.csv''')
    exit(0)

with open(sys.argv[1]) as f:
    data= f.read()

fields = {
    'token': config['api_token'],
    'content': 'record',
    'format': 'csv',
    'type': 'flat',
    'data': data,
}

r = requests.post(config['api_url'], data=fields)
print('HTTP Status: ' + str(r.status_code))
print(r.text)

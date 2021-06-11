#!/usr/bin/env python

from config import config
import requests

with open('../../gen-fake-data/fake_data.csv') as f:
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

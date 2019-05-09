#!/usr/bin/env python3

import os
import requests
from collections import Counter
from ruamel.yaml import YAML
import datetime

yaml = YAML(typ='safe')

from argparse import ArgumentParser
import json
import subprocess
import os
import numpy as np

DESCRIPTION = 'This scripts checks one job in detail.'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-s','--status_to_check', help='The mode that you want to check (i.e. failed or succeeded), default: failed', default='failed')
    parser.add_argument('-m','--mode', type=int,help='0: everything get printed, 1 only one, default=1', default=1)
    parser.add_argument('-p','--position', type=int,help='The jobs that match the state get into a array. With this parameter you can scroll to your jobs. Default=-1 := The last job.', default=-1)
    
    args = parser.parse_args()
    
    with open(os.path.expanduser('~/.cache/dvc_cc/secrets.yml')) as f:
        secrets = yaml.load(f)
    
    auth = (secrets['agency_username'], secrets['agency_password'])
    
    with open(os.path.expanduser('~/.cache/dvc_cc/list_of_job_ids.csv')) as f:
        experiment_ids = f.read().splitlines()
    
    batch_ids = []
    
    for i in range(len(experiment_ids)):
        r = requests.get(
            'https://agency.f4.htw-berlin.de/cc/batches?experimentId={}'.format(experiment_ids[i]),
            auth=auth
        )
        r.raise_for_status()
        data = r.json()
    
        batch_id = None
        for batch in data:
            if batch['state'] == args.status_to_check:
                batch_ids.append(batch['_id'])
    
    
    batch_id_times = []
    
    # Search for last batch with this status
    for i in range(len(batch_ids)):
      r = requests.get(
          'https://agency.f4.htw-berlin.de/cc/batches/{}'.format(batch_ids[i]),
          auth=auth
      )
      r.raise_for_status()
      data2 = r.json()
      
      batch_id_times.append(data2['history'][-1]['time'])
    
    positions = np.argsort(batch_id_times)
    
    batch_id = np.array(batch_ids)[positions][args.position]
    
    # get tthe information of this last batch
    r = requests.get(
        'https://agency.f4.htw-berlin.de/cc/batches/{}'.format(batch_id),
        auth=auth
    )
    r.raise_for_status()
    data2 = r.json()
    
    
    
    print(len(batch_ids), ' jobs that have the status'+args.status_to_check+'.')
    print()
    print('The following information are for the last ',args.status_to_check,' job.')
    print('batch_id:  ', batch_id)
    print('used_gpus: ', data2['usedGPUs'], '(',data2['node'],')')
    ts = data2['history'][-1]['time']
    print('timestamp: ', datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
    
    
    if args.mode == 0:
      print(data2)
    elif args.mode == 1:
      print('runned commamd: ', data2['history'][-1]['ccagent']['command'])
      print()
      for k in data2['history'][-1]['ccagent']['process'].keys():
        print('####################',k,'####################')
        r = data2['history'][-1]['ccagent']['process'][k]
        if type(r) is list:
          for i in range(len(r)):
            print(r[i])
        else:
          print(r)
    
        print()
    
    
    
    
    

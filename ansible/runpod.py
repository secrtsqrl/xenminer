#!/usr/bin/env python
import requests
import json
import sys

CUDA = {
    'NVIDIA A30': 80,
    'NVIDIA H100': 90,
    'NVIDIA GeForce RTX 4090': 89,
    'NVIDIA GeForce RTX 3090': 86,
    'NVIDIA L40': 89,
    'NVIDIA RTX A5000': 86,
    'NVIDIA RTX A6000': 86,
}

API_KEY = 'CY9J0XGJ9L05YJRQ54D1V1S53HIHNOTMSLT9FOZ6'

def main():

    r = requests.post(
        'https://api.runpod.io/graphql',
        params = {
            'api_key': API_KEY,
        },
        data = '{"query": "query Pods { myself { pods { id machine { gpuTypeId } runtime { ports { ip publicPort type } gpus { gpuUtilPercent memoryUtilPercent } container { cpuPercent memoryPercent } } } } }"}',
        headers = {
            'content-type': 'application/json',
        }
    )

    hosts = {}
    hostvars = {}
    for pod in r.json()['data']['myself']['pods']:
        pod_id = pod['id']

        try:
            group, hostname, host = pod2ansible(pod)
        except Exception as e:
            print(f'{pod_id}: {e}', file=sys.stderr)
            continue

        if group in hosts:
            group = hosts[group]
        else:
            hosts[group] = group = { 'hosts': [] }

        group['hosts'].append(hostname)
        hostvars[hostname] = host

    hosts['_meta'] = {
        'hostvars': hostvars
    }

    print(json.dumps(hosts))

def pod2ansible(pod):
    pod_id = pod['id']
    gpu = pod['machine']['gpuTypeId']
    group = gpu.replace(' ', '_')
    hostname = f'{pod_id}_{group}'

    try:
        tcp = next(x for x in pod['runtime']['ports'] if x['type'] == 'tcp')
    except:
        raise Exception('no tcp port')

    return group, hostname, {
        'ansible_host': tcp['ip'],
        'ansible_port': tcp['publicPort'],
        'gpus': pod['runtime']['gpus'],
        'container': pod['runtime']['container'],
        'cuda': CUDA[gpu],
        'ansible_user': 'root',
    }

main()


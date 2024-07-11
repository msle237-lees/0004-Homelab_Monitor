from pyspectator import Computer
from pyspectator.processor import Cpu
from pyspectator.memory import Memory
from pyspectator.network import Network

import shutil

import argparse
import requests
import json

class Client:
    def __init__(self, url):
        self.computer = Computer()
        self.cpu = Cpu()
        self.memory = Memory()
        self.network = Network()
        self.url = url

    def get_disk_usage(self):
        total, used, free = shutil.disk_usage("/")
        return {
            'total': total,
            'used': used,
            'free': free
        }

    def get_server_stats(self):
        disk_usage = self.get_disk_usage()
        server_stats = {
            'cpu_usage': self.cpu.usage,
            'ram_usage': self.memory.used,
            'disk_total': disk_usage['total'], # 'disk_total' is the total disk space, 'disk_used' is the used disk space, 'disk_free' is the free disk space
            'disk_free': disk_usage['free'],
            'disk_usage': disk_usage['used'],
            'network_usage': self.network.bytes_sent + self.network.bytes_recv
        }
        return server_stats

    def add_server_stat(self, server_id, cpu_usage, ram_usage, disk_usage, network_usage):
        url = self.url + '/add_server_stat'
        data = {
            'server_id': server_id,
            'cpu_usage': cpu_usage,
            'ram_usage': ram_usage,
            'disk_total': disk_usage['total'],
            'disk_free': disk_usage['free'],
            'disk_usage': disk_usage,
            'network_usage': network_usage
        }

        response = requests.post(url, data=data)
        return response
    
    def set_server_id(self, server_id):
        self.server_id = server_id

    def run(self):
        server_stats = self.get_server_stats()
        self.add_server_stat(self.server_id, server_stats['cpu_usage'], server_stats['ram_usage'], server_stats['disk_usage'], server_stats['network_usage'])

    def start(self, server_id, url):
        self.computer.enable()
        self.cpu.enable()
        self.memory.enable()
        self.disk.enable()
        self.network.enable()

        self.set_server_id(server_id)
        self.url = url

        while True:
            self.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client for monitoring server stats')
    parser.add_argument('--url', type=str, help='The URL of the server to send stats to')
    parser.add_argument('--server_id', type=int, help='The ID of the server to send stats to')

    args = parser.parse_args()

    client = Client(args.url)
    client.set_server_id(args.server_id)
    client.run()

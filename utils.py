import os
import psutil
import json
import requests as rq

from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM


class sysInfo:
    @staticmethod
    def get_local_ip() -> str:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip

    @staticmethod
    def get_external_ip() -> str:
        return rq.get("https://httpbin.org/ip").json()['origin']

    @staticmethod
    def get_tcp_connections() -> int:
        connections = psutil.net_connections(kind='inet')
        return len([conn for conn in connections if conn.status == psutil.CONN_ESTABLISHED and conn.type == SOCK_STREAM])

    @staticmethod
    def get_udp_connections() -> int:
        connections = psutil.net_connections(kind='inet')
        return len([conn for conn in connections if conn.status == psutil.CONN_NONE and conn.type == SOCK_DGRAM])

    @staticmethod
    def get_disks() -> dict:
        partitions = psutil.disk_partitions()
        disk_info = []

        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                'root': partition.device,
                'total': usage.total,
                'free': usage.free
            })

        return disk_info

    @staticmethod
    def get() -> dict:
        return {
            "extIP": sysInfo.get_external_ip(),
            "locIP": sysInfo.get_local_ip(),
            "tcpconns": sysInfo.get_tcp_connections(),
            "udpconns": sysInfo.get_udp_connections(),
            "disks": sysInfo.get_external_ip(),
        }


def config_file_exists_decorator(func):
    def wrapper(self, *args, **kwargs):

        if not os.path.isfile(self.file):
            json.dump(self.data, open(self.file, 'w'), indent=self.indent)
            print(f'Initialized default config file at {self.file}')

        return func(self, *args, **kwargs)

    return wrapper


class Config:
    def __init__(self, filepath: str, default: dict = {}, indent: str = 4, debug: bool = False, set_default: bool = False):
        self.file = filepath
        self.default = default
        self.indent = indent
        self.debug = debug
        self.last_data = {}

        if 'debug' in self.data.keys():
            self.debug = self.data['debug']

        if not os.path.isfile(self.file) or set_default:
            json.dump(default, open(self.file, 'w'), indent=self.indent)
            if self.debug:
                print(f'Initialized default config file at {self.file}')


    @config_file_exists_decorator
    def change(self, **kwargs):
        content = json.load( open(self.file, 'r') )
        first = json.load( open(self.file, 'r') )


        for key, value in kwargs.items():
            keys = key.split("__")
            self._update_nested(content, keys, value)


        json.dump(content, open(self.file, 'w'), indent=self.indent)

        if self.debug:
            for key, value in first.items():
                if not key in content.keys():
                    print(f"Added new key: {key}={value}")
                else:
                    if value != content[key]:
                        print(f"Changed value for {key}, from {value} to {content[key]}")

            for key, value in content.items():
                if not key in first.keys():
                    print(f"Removed key: {key}={value}")
        self.last_data = json.load( open(self.file, 'r') )

    @config_file_exists_decorator
    def move_to(self, filepath: str):
        data = self.data
        last_path =  self.file
        self.file = filepath

        if os.path.isfile(last_path):
            os.remove(last_path)

        json.dump(data, open(self.file, 'w'), indent=self.indent)

        self.last_data = json.load( open(self.file, 'r') )
        if self.debug:
            print(f"Moved file from {last_path} ro {self.file}")

    @config_file_exists_decorator
    def read(self, keys: list = []) -> dict:
        if keys:
            return { key: value for key, value in json.load( open(self.file, 'r') ).items() if key in keys }

        self.last_data = json.load( open(self.file, 'r') )
        return dict(self.last_data)

    @property
    def data(self) -> dict:
        return self.read()

    def _update_nested(self, dictionary: dict, keys: list, value):
        if len(keys) == 1:
            dictionary[keys[0]] = value
        else:
            first_key, remaining_keys = keys[0], keys[1:]
            if first_key not in dictionary:
                dictionary[first_key] = {}
            self._update_nested(dictionary[first_key], remaining_keys, value)
    

    def __str__(self):
        return json.dumps(self.data, indent=self.indent)

    def __dict__(self):
        return self.data
    def __getitem__(self, key):
        return self.data[key]

    def __list__(self):
        return self.data.keys()

    def __repr__(self):
        return f"Config(file={self.file}, data={self.data})"


if __name__ == '__main__':
    print(sysInfo().get())
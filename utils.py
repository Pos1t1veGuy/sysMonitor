import os
import psutil
import json


class sysInfo:
    def __init__(self, cpuram_update_rate: int = 100,
            disks_update_rate: int = 100,
            nets_update_rate: int = 100,
            ):
        self.cpuram_update_rate = cpuram_update_rate
        self.disks_update_rate = disks_update_rate
        self.nets_update_rate = nets_update_rate

    def get_local_ip(self) -> str:
        return "xx.xx.xx.xx"

    def get_external_ip(self) -> str:
        return "xx.xx.xx.xx"

    def get_tcp_connections(self) -> int:
        return 0

    def get_udp_connections(self) -> int:
        return 0

    def get_disks(self) -> dict:
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

    def get_ram(self) -> int:
        " RAM load percent "
        return 93

    def get_cpu(self) -> int:
        " CPU load percent "
        return 98

    def get(self) -> dict:
        return {
            "extIP": self.get_external_ip(),
            "locIP": self.get_local_ip(),
            "tcpconns": self.get_tcp_connections(),
            "udpconns": self.get_udp_connections(),
            "disks": self.get_external_ip(),
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

        if not os.path.isfile(self.file) or set_default:
            json.dump(default, open(self.file, 'w'), indent=self.indent)
            print(f'Initialized default config file at {self.file}')

        if 'debug' in self.data.keys():
            self.debug = self.data['debug']


    @config_file_exists_decorator
    def change(self, **kwargs):
        content = json.load( open(self.file, 'r') )
        first = json.load( open(self.file, 'r') )

        for key, value in kwargs.items():
            content[key] = value

        json.dump(content, open(self.file, 'w'), indent=self.indent)

        if self.debug:
            for key, value in first.items():
                if not key in content.keys():
                    print(f"Added new key: {key}={value}")
                else:
                    if value != content[key]:
                        print(f"Changed value for key {key}, from {value} to {content[key]}")

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
    

    def __str__(self):
        return str(self.data)

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
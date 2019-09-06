import json
from shutil import copyfile
from os import listdir
import os.path

DATADIR = os.path.join(os.path.expanduser("~"), ".junction/")

def full_path(relative_path):
    return os.path.join(DATADIR, relative_path)

def write_json_file(data, relative_path):
    path = full_path(relative_path)
    with open(path, 'w') as f:
        return json.dump(data, f, indent=4)

def read_json_file(relative_path):
    path = full_path(relative_path)
    with open(path, 'r') as f:
        return json.load(f)

def ensure_datadir():
    if not os.path.isdir(DATADIR):
        # make datadir
        os.mkdir(DATADIR)
        # make wallets directory inside datadir
        wallets_dir = os.path.join(DATADIR, 'wallets')
        os.mkdir(wallets_dir)
        # copy settings.json to datadir
        settings_path = full_path('settings.json')
        copyfile('settings.json.ex', settings_path)

def get_settings():
    return read_json_file('settings.json')

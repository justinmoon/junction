import json
from shutil import copyfile
from os import listdir
import os.path

DATADIR = os.path.join(os.path.expanduser("~"), ".junction/")

def full_path(relative_path):
    return os.path.join(DATADIR, relative_path)

def write_json_file(data, relative_path):
    path = full_path(relative_path)
    serialized = json.dumps(data, indent=4, sort_keys=True)
    with open(path, 'w') as f:
        f.write(serialized)

def read_json_file(relative_path):
    path = full_path(relative_path)
    with open(path, 'r') as f:
        return json.load(f)

def ensure_datadir():
    if not os.path.isdir(DATADIR):
        # make datadir
        os.mkdir(DATADIR)

    wallet_dir = full_path('wallets')
    if not os.path.isdir(wallet_dir):
        # make wallets directory inside datadir
        os.mkdir(wallet_dir)

def get_wallet_names():
    wallet_names = []
    wallets_dir = os.path.join(DATADIR, 'wallets')
    wallet_files = os.listdir(wallets_dir)
    for wallet_file in wallet_files:
        wallet_name = wallet_file.split('.')[0]
        wallet_names.append(wallet_name)
    return wallet_names

def get_wallets():
    from junction import Wallet  # FIXME: circular imports
    wallets = []
    wallet_names = get_wallet_names()
    for wallet_name in wallet_names:
        wallet = Wallet.open(wallet_name, ensure_watchonly=False)
        wallets.append(wallet)
    return wallets



import atexit
import subprocess
import tempfile
import shutil
import os
import json
import time
import unittest

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def start_bitcoind(bitcoind_path):
    datadir = tempfile.mkdtemp()
    bitcoind_proc = subprocess.Popen([bitcoind_path, '-regtest', '-datadir=' + datadir, '-noprinttoconsole'])
    def cleanup_bitcoind():
        bitcoind_proc.kill()
        shutil.rmtree(datadir)
    atexit.register(cleanup_bitcoind)
    # Wait for cookie file to be created
    while not os.path.exists(datadir + '/regtest/.cookie'):
        time.sleep(0.5)
    # Read .cookie file to get user and pass
    with open(datadir + '/regtest/.cookie') as f:
        rpc_username, rpc_password = f.readline().lstrip().rstrip().split(':')
    rpc = AuthServiceProxy('http://{}:{}@127.0.0.1:18443/wallet/'.format(rpc_username, rpc_password))

    # Wait for bitcoind to be ready
    ready = False
    while not ready:
        try:
            rpc.getblockchaininfo()
            ready = True
        except JSONRPCException as e:
            time.sleep(0.5)
            pass

    # Make sure there are blocks and coins available
    rpc.generatetoaddress(101, rpc.getnewaddress())
    return (rpc, rpc_username, rpc_password)

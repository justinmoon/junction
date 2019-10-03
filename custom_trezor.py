'''
https://pypi.org/project/trezor/

pip3 install --upgrade setuptools
pip3 install trezor[hidapi]
'''


# import trezorlib.messages as proto
# from trezorlib.client import TrezorClient
# from trezorlib.transport import get_transport
# from trezorlib.btc import get_address
# from trezorlib.tools import parse_path
# from trezorlib.ui import ClickUI

from hwilib import commands
from hwilib.devices import trezorlib
from hwilib.devices.trezor import parse_multisig, proto

def show_address_hwi():
    address_path = trezorlib.tools.parse_path("m/48'/1'/0'/2'/0/1")
    redeem_script = bytes.fromhex('5221029d1d099ca83088773688173ac0989281f22d896f570576746501f4897e45053921031ec3335f071ead775abd05ece6e215642a260eb5c65c8a5572681c27b5fd76f852ae')
    multisig = parse_multisig(redeem_script)
    assert multisig[0]
    multisig = multisig[1]
    
    script_type = proto.InputScriptType.SPENDP2SHWITNESS
    # script_type = proto.TxInputType()
    # script_type.multisig = multisig
    script_type = proto.InputScriptType.SPENDMULTISIG
    script_type = proto.InputScriptType.SPENDWITNESS
    print(multisig)
    client = commands.get_client(device_type, device_path)
    client.client.init_device()
    a = trezorlib.btc.get_address(
        client.client,
        'Testnet',
        address_path,
        show_display=True,
        script_type=script_type,
        multisig=multisig,
    )
    print(a)


def display_multisig_address(redeem_script_hex, derivation_path_str, testnet, device):
    print(redeem_script_hex)
    print(derivation_path_str)
    print(testnet)
    print(device)
    # translate to formats required by Trezor
    derivation_path = trezorlib.tools.parse_path(derivation_path_str)
    redeem_script = bytes.fromhex(redeem_script_hex)
    
    # get multisig object required by Trezor's get_address
    multisig = parse_multisig(redeem_script)
    print(multisig)
    assert testnet
    assert multisig[0]
    multisig = multisig[1]

    # script type (native segwit for now)
    script_type = proto.InputScriptType.SPENDWITNESS

    # create client and send request
    client = commands.get_client('trezor', device['path'])
    client.client.init_device()  # fails without this
    trezorlib.btc.get_address(
        client.client,
        'Testnet' if testnet else 'Bitcoin',
        derivation_path,
        show_display=True,
        script_type=script_type,
        multisig=multisig,
    )

if __name__ == '__main__':
    raw_derivation_path = "m/48'/1'/0'/2'/0/1"
    redeem_script_hex = '5221029d1d099ca83088773688173ac0989281f22d896f570576746501f4897e45053921031ec3335f071ead775abd05ece6e215642a260eb5c65c8a5572681c27b5fd76f852ae'
    testnet = True
    from utils import get_device
    device = get_device("7209ddfa")
    display_multisig_address(redeem_script_hex, raw_derivation_path, testnet, device)
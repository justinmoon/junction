"""
TODO
- add a "decodepsbt" command
"""
import argparse
import glob
import logging
from decimal import Decimal
from pprint import pprint

from hwilib import commands
from hwilib.devices import coldcard, digitalbitbox, ledger

from junction import MultiSig
from signer import HardwareSigner

logger = logging.getLogger(__name__)


def display_wallet(multisig):
    print(f"Name: {multisig.name} {multisig.m}/{multisig.n}")
    if len(multisig.signers) > 0:
        print("Signers:")
        for signer in multisig.signers:
            print(f"- \"{signer.name}\" ({signer.type})")
    if not multisig.ready():
        signers_missing = multisig.n - len(multisig.signers)
        print(f"You must register {signers_missing} signers to start using your wallet")


def describewallet_handler(args):
    multisig = MultiSig.open(args.filename)
    display_wallet(multisig)


def listwallets_handler(args):
    for filename in glob.glob("*.json"):
        multisig = MultiSig.open(filename)
        display_wallet(multisig)
        print()


def addsigner_handler(args):
    multisig = MultiSig.open(args.filename)
    devices = commands.enumerate(args.password)

    if not devices:
        print('No devices available. Enter your pin if device already plugged in')
        return

    if len(devices) > 1:
        print('You can only plug in one device at a time')

    # Check this device hasn't been used yet
    device = devices[0]
    fingerprints = [signer.fingerprint for signer in multisig.signers]
    if device['fingerprint'] in fingerprints:
        print('This device is already registered')
        return

    # Check this name hasn't been used yet
    names = [signer.name for signer in multisig.signers]
    if args.name in names:
        print('This name has already been used')
        return

    # Define an HWI "client" based on depending on which device is plugged in
    if device['type'] == 'ledger':
        client = ledger.LedgerClient(device['path'])
    elif device['type'] == 'digitalbitbox':
        if not args.password:
            print('Please supply your BitBox password with the --password flag')
            return
        client = digitalbitbox.DigitalbitboxClient(device['path'], args.password)
    else:
        print(f'Devices of type "{device["type"]}" not yet supported')

    # Set device client to use testnet
    client.is_testnet = True

    # Create and add a "signer" to the wallet
    xpub = commands.getmasterxpub(client)['xpub']
    signer = HardwareSigner(args.name, device['path'], device['fingerprint'], xpub)
    multisig.add_signer(signer)
    print(f"Signer \"{signer.name}\" has been added to your \"{multisig.name}\" wallet")

    # Print messages depending on whether the setup is complete or not
    if multisig.ready():
        print(f"Wallet \"{multisig.name}\" is ready to use. Your first receiving address:")
        print(multisig.address())
    else:
        signers_missing = multisig.n - len(multisig.signers)
        print(f"Add {signers_missing} more signers to start using it")


def address_handler(args):
    multisig = MultiSig.open(args.filename)
    print(multisig.address())


def createwallet_handler(args):
    multisig = MultiSig.create(args.name, args.m, args.n)
    print(f"Your new {multisig.m}/{multisig.n} wallet has been saved to \"{multisig.filename()}\"")


def createpsbt_handler(args):
    multisig = MultiSig.open(args.filename)
    multisig.create_psbt(args.recipient, args.amount)
    print("You PSBT for wallet \"{multisig.name}\" has been created:")

def decodepsbt_handler(args):
    multisig = MultiSig.open(args.filename)
    pprint(multisig.decode_psbt())
    

def cli():
    # main parser
    parser = argparse.ArgumentParser(description='Junction Multisig Bitcoin Wallet')
    parser.add_argument('--debug', help='Print debug statements', action='store_true')
    # FIXME: user should have to explicitly specify this if there are more than 1 wallet
    parser.add_argument('--wallet', help='Wallet to use (default: "junction")', default="junction")

    # subparsers
    subparsers = parser.add_subparsers(help='sub-command help')

    # "junction describewallet"
    describewallet_parser = subparsers.add_parser('describewallet', help='Displays state of a wallet')
    describewallet_parser.set_defaults(func=describewallet_handler)

    # "junction listwallets"
    listwallets_parser = subparsers.add_parser('listwallets', help='Displays state of all wallet')
    listwallets_parser.set_defaults(func=listwallets_handler)

    # "junction createwallet n m"
    createwallet_parser = subparsers.add_parser('createwallet', help='Create a multisig wallet')
    createwallet_parser.add_argument('m', type=int, help='Signatures required to sign transactions')
    createwallet_parser.add_argument('n', type=int, help='Total number of signers')
    createwallet_parser.add_argument('--name', help='What to call this wallet', default="junction")
    createwallet_parser.set_defaults(func=createwallet_handler)

    # "junction addsigner"
    addsigner_parser = subparsers.add_parser('addsigner', help='Add signers to your multisig wallet')
    addsigner_parser.add_argument('name', help='What to call this signer')
    addsigner_parser.add_argument('--password', default='', help='Device password (required for BitBox)')
    addsigner_parser.set_defaults(func=addsigner_handler)

    # "junction address"
    address_parser = subparsers.add_parser('address', help='Show next receiving address')
    address_parser.set_defaults(func=address_handler)

    # "junction createpsbt"
    createpsbt_parser = subparsers.add_parser('createpsbt', help='Create a Partially Signed Bitcoin Transaction (PSBT)')
    createpsbt_parser.add_argument('recipient', help='Bitcoin address to send funds')
    createpsbt_parser.add_argument('amount', type=Decimal, help='How many BTC to send')
    createpsbt_parser.set_defaults(func=createpsbt_handler)

    # "junction decodepsbt"
    decodepsbt_parser = subparsers.add_parser('decodepsbt', help='Show more information about your PSBT')
    decodepsbt_parser.set_defaults(func=decodepsbt_handler)

    # "junction signpsbt"

    # parse args
    args = parser.parse_args()
    args.filename = args.wallet + '.json'  # HACK

    # housekeeping
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)

    # exercise callback
    # TODO: perhaps I could instantiate MultiSig() instance here and pass to args.func?
    return args.func(args)

if __name__ == '__main__':
    cli()

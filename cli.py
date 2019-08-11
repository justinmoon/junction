import argparse
import glob
import logging
import contextlib
import io

from decimal import Decimal
from pprint import pprint
from hwilib import commands, serializations
from hwilib.devices import coldcard, digitalbitbox, ledger, trezor

from junction import MultiSig, JunctionError

logger = logging.getLogger(__name__)


def display_wallet(multisig):
    print(f"Name: {multisig.name} {multisig.m}/{multisig.n}")
    if len(multisig.signers) > 0:
        print("Signers:")
        for signer in multisig.signers:
            print(f"- \"{signer['name']}\"")
    if not multisig.ready():
        signers_missing = multisig.n - len(multisig.signers)
        print(f"You must register {signers_missing} signers to start using your wallet")
    multisig.export_watchonly()


def get_client_and_device(args, multisig):

    # Make sure one and only one device is plugged in
    devices = commands.enumerate(args.password)
    if not devices:
        raise JunctionError('No devices available. Enter your pin if device already plugged in')
    if len(devices) > 1:
        raise JunctionError('You can only plug in one device at a time')
    device = devices[0]

    # Can't instantiate bitbox client w/o pasphrase, so this needs to be before next block
    if device.get("needs_passphrase_sent") and not args.password:
        raise JunctionError('Please supply your device password with the --password flag')

    # Define an HWI "client" based on depending on which device is plugged in
    if device['type'] == 'ledger':
        client = ledger.LedgerClient(device['path'])
    elif device['type'] == 'digitalbitbox':
        client = digitalbitbox.DigitalbitboxClient(device['path'], args.password)
    elif device['type'] == 'coldcard':
        client = coldcard.ColdcardClient(device['path'])
    elif device['type'] == 'trezor':
        client = trezor.TrezorClient(device['path'])
    else:
        raise JunctionError(f'Devices of type "{device["type"]}" not yet supported')
    client.is_testnet = True

    # this requires a client, so it needs to come after previous block
    if device.get('needs_pin_sent'):
        # this prints to stderr ... suppress it
        with contextlib.redirect_stderr(io.StringIO()):
            client.prompt_pin()

        pin = input("Use the numeric keypad to enter your pin. The layout is:\n\t7 8 9\n\t4 5 6\n\t1 2 3\nPin: ")
        if not client.send_pin(pin)["success"]:
            raise JunctionError('Pin is wrong')

        # FIXME: device dict has not "fingerprint" key and we calling commands.enumerate() again throws error
        # This hack retrievs and sets it manually
        import time
        time.sleep(1)
        device['fingerprint'] = commands.get_xpub_fingerprint_as_id(commands.getxpub(client, 'm/0h')['xpub'])

    # FIXME: Commenting out for now because device variable is outdated in "needs_pin_sent" case and I can't manage to refresh it ...
    # Get updated "device" (prior value may lack "fingerprint" if device was locked)
    # if device.get("error"):
        # raise JunctionError(f"Unexpected error: {device['error']}")

    return client, device


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
    client, device = get_client_and_device(args, multisig)

    # Create and add a "signer" to the wallet
    master_xpub = client.get_pubkey_at_path('m/0h')['xpub']
    origin_path = "m/44h/1h/0h"
    base_key = client.get_pubkey_at_path(origin_path)['xpub']
    multisig.add_signer(args.name, device['fingerprint'], base_key, origin_path)
    print(f"Signer \"{args.name}\" has been added to your \"{multisig.name}\" wallet")

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
    if multisig.psbt:
        user_input = input("You already have a PSBT. Would you like to erase it and start a new one? (y/n)")
        if user_input == 'y':
            multisig.remove_psbt()
        else:
            print("Cancelled")
            return
    multisig.create_psbt(args.recipient, args.amount)
    print(f"Your PSBT for wallet \"{multisig.name}\" has been created")
    print("View it with \"python cli.py decodepsbt\"")

def decodepsbt_handler(args):
    multisig = MultiSig.open(args.filename)
    pprint(multisig.decode_psbt())

def signpsbt_handler(args):
    multisig = MultiSig.open(args.filename)
    client, device = get_client_and_device(args, multisig)
    psbt = multisig.psbt
    raw_signed_psbt = client.sign_tx(multisig.psbt)['psbt']
    new_psbt = serializations.PSBT()
    new_psbt.deserialize(raw_signed_psbt)
    multisig.psbt = new_psbt
    multisig.save()
    
def broadcast_handler(args):
    multisig = MultiSig.open(args.filename)
    txid = multisig.broadcast()
    print("Transaction ID:", txid)

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
    signpsbt_parser = subparsers.add_parser('signpsbt', help='Sign your PSBT')
    # FIXME: this should probably live on base parser
    signpsbt_parser.add_argument('--password', default='', help='Device password (required for BitBox)')
    signpsbt_parser.set_defaults(func=signpsbt_handler)

    # "junction broadcast"
    broadcast_parser = subparsers.add_parser('broadcast', help='Broadcast your signed PSBT')
    broadcast_parser.set_defaults(func=broadcast_handler)

    # parse args
    args = parser.parse_args()
    args.filename = f'{args.wallet}.json'  # HACK

    # housekeeping
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)

    # exercise callback
    # TODO: pass in multisig and client
    # these functions are very CLI-specific with the `args` variables
    # how to generalize them so they'd work with flask as well?
    try:
        args.func(args)
    except JunctionError as e:
        print(e)

if __name__ == '__main__':
    cli()

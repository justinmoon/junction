import argparse
import glob
import logging

from junction import MultiSig
from signer import InsecureSigner

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
    print("one time export")
    multisig.watch_only_export()


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
    signer = InsecureSigner.create(args.name)
    multisig.add_signer(signer)
    print(f"Signer \"{signer.name}\" has been added to your \"{multisig.name}\" wallet")
    if multisig.ready():
        print(f"Wallet \"{multisig.name}\" is ready to use. Your first receiving address:")
        print(multisig.address())
    else:
        signers_missing = multisig.n - len(multisig.signers)
        print(f"Add {signers_missing} more signers to start using it")


def receive_handler(args):
    multisig = MultiSig.open(args.filename)
    print(multisig.address())


def create_handler(args):
    multisig = MultiSig.create(args.name, args.m, args.n)
    print(f"Your new {multisig.m}/{multisig.n} wallet has been saved to \"{multisig.filename()}\"")


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

    # "junction create n m"
    create_parser = subparsers.add_parser('create', help='Create a multisig wallet')
    create_parser.add_argument('m', type=int, help='Signatures required to sign transactions')
    create_parser.add_argument('n', type=int, help='Total number of signers')
    create_parser.set_defaults(func=create_handler)
    create_parser.add_argument('--name', help='What to call this wallet', default="junction")

    # "junction addsigner"
    addsigner_parser = subparsers.add_parser('addsigner', help='Add signers to your multisig wallet')
    addsigner_parser.add_argument('name', help='What to call this signer')
    addsigner_parser.set_defaults(func=addsigner_handler)

    # "junction receive"
    receive_parser = subparsers.add_parser('receive', help='Show next receiving address')
    receive_parser.set_defaults(func=receive_handler)

    # "junction newpsbt"

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

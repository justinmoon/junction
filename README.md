# Junction

## Requirements

- A Ledger with the "testnet" app installed. To install:
    - Open "Ledger Live" desktop app
    - Click the settings gear icon in top right
    - Click "Experimental features" tab at top
    - Enable "Developer mode"
    - Click the "Manager" tab on left
    - Enter ledger pin and accept the "Allow Ledger manager?" prompt on device screen
    - Search for and install the "Bitcoin Test" app
- A BitBox
    - You'll need your device password

## Setup

I've been playing with [Bitcoinlib](https://bitcoinlib.readthedocs.io/en/latest/source/bitcoinlib.wallets.html) which makes the dependencies very bloated. I'll remove it soon!

```
# Copy example settings file and enter in your RPC credentials
cp settings.toml.ex settings.toml

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run bitcoin-qt in testnet mode
bitcoin-qt -testnet
```

## Usage

To create a 2/2 wallet:

```
# Create a wallet
python cli.py createwallet 2 2

# Plug in Ledger, enter pin, navigate to testnet app
# Add Ledger "signer" to wallet
python cli.py addsigner <name-for-this-device>

# Unplug Ledger and plug in BitBox
# Add BitBox "signer" to wallet
python cli.py addsigner <name-for-this-device> --password <bitbox-password>
```

The last step should display an address. Send some TBTC to this address and it should show up bitcoin-qt. The `createwallet` step above created a watch-only wallet in Bitcoin Core and exported addresses to it. Load this wallet in the UI by clicking `File > Open Wallet > junction`. Your coins should show up in the receiving tab.

Some metadata about your wallet is stored in plain text JSON in `junction.wallet`.

I'm working to add PSBT signing. This is the intended workflow:

```
# Initialize a PSBT using Bitcoin Core's coin selection
python cli.py createpsbt <recipient-address> <amount-in-tbtc>

# Plug in Ledger, confirm transaction on device, update PSBT w/ Ledger signature
python cli.py signpsbt

# Plug in BitBox, confirm transaction on device, update PSBT w/ BitBox signature
python cli.py signpsbt --password <bitbox-password>

# Broadcast to network
python cli.py broadcast
```

## Notes

### ColdCard

- Threw a "fraudulent change output" error when bitcoind isn't run
  with `-addresstype=bech32 -changetype=bech32` flags
- When attempting a to sign a non-multisig output, ColdCard threw an error having to do with paths. I bet our descriptor xpubs need a fingerprints and path prefixes like in the last step [here](https://gist.github.com/achow101/a9cf757d45df56753fae9d65db4d6e1d).
- [This guide](https://github.com/bitcoin-core/HWI/blob/master/docs/bitcoin-core-usage.md) is very helpful.


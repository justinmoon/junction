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

## Usage

To create a wallet 2/3:

```
python cli.py createwallet 2 3

# Plug in Ledger, enter pin, navigate to testnet app
python cli.py addsigner <name-for-this-device>

# Unplug Ledger and plug in BitBox
python cli.py addsigner <name-for-this-device> --password <bitbox-password>
```

The last step should display an address. Send some TBTC to this address and then open up bitcoin-qt in testnet mode (`bitcoin-qt -testnet`). The `createwallet` step above created a watch-only wallet in Bitcoin Core and exported addresses to it. Load this wallet in the UI by clicking `File > Open Wallet > junction`. Your coins should show up in the receiving tab.

I'm working to add PSBT signing. This is the intended workflow:

```
python cli.py createpsbt <recipient-address> <amount-in-tbtc>

# Plug in Ledger
python cli.py signpsbt

# Plug in BitBox
python cli.py signpsbt

python cli.py broadcast
```

First step creates an PSBT spending inputs chosen by Bitcoin Core's coin selection algorithm.

Second and third steps update the PSBT with signatures from hardware devices.

Final step "finalizes" the PSBT and broadcasts it via Bitcoin Core.

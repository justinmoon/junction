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
## Create a 3/3 Wallet using Trezor, Ledger & BitBox

Demostration that these 3 devices work. Other numbers for m and n should work. I don't have a KeepKey to test with and still working to add ColdCard soon (currently getting a `hwilib.errors.BadArgumentError: Remote Error: Invalid PSBT: Missing redeem script for output #i` error if any kind can reproduce or help debug).

### Wallet Creation

```
# Create 3/3 wallet
$ python cli.py createwallet 3 3
Your new 3/3 wallet has been saved to "junction.wallet"

# Plug in Ledger, enter PIN, navigate to testnet app
# Add Ledger "signer" to wallet
$ python cli.py addsigner <ledger-nickname>
Signer "<ledger-nickname>" has been added to your "junction" wallet
Add 2 more signers to start using it

# Unplug Ledger and plug in BitBox
# Add BitBox "signer" to wallet
$ python cli.py addsigner <bitbox-nickname> --password <bitbox-password>
Signer "<bitbox-nickname>" has been added to your "junction" wallet
Add 1 more signers to start using it

# Unplug BitBox and plug in Trezor
# Add Trezor "signer" to wallet
# Pin shown is what you'd enter in case pictured below:
$ python cli.py addsigner <trezor-nickname>
Use the numeric keypad to enter your pin. The layout is:
	7 8 9
	4 5 6
	1 2 3
Pin: 362751984
Signer "<trezor-nickname>" has been added to your "junction" wallet
Wallet "junction" is ready to use. Your first receiving address:
<receiving-address>
```

Send some TBTC to `<receiving-address>` If you have bitcoin-qt open you should see a notification that it was received. Here's a [testnet faucet](https://testnet-faucet.mempool.co/) if you don't have any TBTC on hand.

The `createwallet` step above created a watch-only wallet in Bitcoin Core and exported addresses to it. Load this wallet in the UI by clicking `File > Open Wallet > junction`. Your coins should show up in the receiving tab.

Some metadata about your wallet is stored in plain text JSON in `junction.wallet`.

### Spending

```
# Once your transaction has confirmed, create a PSBT:
$ python cli.py createpsbt <recipient> <amount-in-btc>
Your PSBT for wallet "junction" has been created

# Plug in Trezor
# Pin entry same as last time (no pin required if you left it in)
$ python cli.py signpsbt
Use the numeric keypad to enter your pin. The layout is:
	7 8 9
	4 5 6
	1 2 3
Pin: 362751984
Please confirm action on your Trezor device

# Unplug Trezor, plug in BitBox. BitBox needs a passphrase:
$ python cli.py signpsbt --password <bitbox-password>
Touch the device for 3 seconds to sign. Touch briefly to cancel

# Unplug BitBox, plug in Ledger, enter PIN, navigate to testnet app:
$ python cli.py signpsbt

# Broadcast transaction
$ python cli.py broadcast
```

You should see an outgoing transaction in the "Transacions" tab in your "junction" watch-only Bitcoin Core wallet

![image](https://wiki.trezor.io/images/User-manual_trezor-pin.jpg)


## TODO:

- Make a simple UI
- Allow multiple devices plugged in at once
- Unittests
- Option to use regtest. These 20 minute testnet blocktime almost killed me today!
- Export change addresses to Bitcoin Core

## Useful Resources:

- [This HWI + Bitcoin Core guide](https://github.com/bitcoin-core/HWI/blob/master/docs/bitcoin-core-usage.md) is very helpful.

## Regtest

Add this to you `bitcoin.conf`:

```
[regtest]
rpcbind=127.0.0.1
rpcallowip=0.0.0.0/0
rpcport=18444
rpcuser=bitcoin
rpcpassword=python
```

Change the `port` variable in `settings.toml` to 18444 (regtest port)

Run bitcoin-qt in regtest mode:

```
bitcoin-qt -regtest
```

Generate some blocks to yourself

```
addr=$(bitcoin-cli -regtest getnewaddress)
bitcoin-cli -regtest generatetoaddress 150 $addr
```

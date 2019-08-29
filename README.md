# Junction: UI For Multisig With Bitcoin Core

![image](./logo.jpg)

## Usage

Junction project uses [HWI](https://github.com/bitcoin-core/HWI) to communicate with hardware wallets. Follow [these instructions](https://github.com/bitcoin-core/HWI#prerequisites) to install dependencies for HWI. If you're on Linux you may need to install udev rules.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
bitcoind -testnet
python ui.py
```

## Features

- Supports P2SH multisig with Trezor, Ledger, and ColdCard hardware wallets
- Connects directly to your full node and monitors balance using watch-only Bitcoin Core wallet
- No javascript, minimal python dependencies

## Limitations

_This is buggy, alpha, proof-of-concept software_

- Testnet-only
- No tests
- Doesn't currently use javascript, so frequent page reloads are required and UX kinda sucks
- Doesn't support P2WSH (ColdCard has a P2WSH bug right now preventing it)
- BIP32 derivation paths hard-coded
- Only 1 wallet allowed at-a-time
- Only 1 PSBT allowed at a time
- ColdCard must be last signer added because we must upload a multisig enrollment file containing the other xpubs.
- Bitcoin Core Limitations:
    - Unconfirmed balances not correctly displayed. `getbalance` and `getunconfirmedbalance` can't find unconfirmed outputs for watch-only wallets in Bitcoin Core 18.1. A new `getbalances` API will fix this in next Bitcoin Core release.
- HWI limitations:
    - [No change detection](https://github.com/bitcoin-core/HWI/issues/170#issuecomment-491843963)
    - Cannot display multisig receiving addresses on hardware wallet display
    - Sometimes HWI thinks wallets are locked when they clearly aren't

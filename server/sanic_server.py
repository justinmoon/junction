from sanic import Sanic
from sanic.response import json
from hwilib import commands
from disk import get_wallets

app = Sanic()

@app.route('/devices')
async def list_devices(request):
    return json(commands.enumerate())

@app.route('/wallets')
async def list_wallets(request):
    # TODO: does this include addresses?
    wallets = get_wallets()
    # FIXME: probably shouldn't include xpubs in this response?
    wallet_dicts = [wallet.to_dict(True) for wallet in wallets]
    return json(wallet_dicts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
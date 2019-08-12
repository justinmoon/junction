from hwilib import commands
from hwilib.devices import trezor

devices = commands.enumerate()

for device in devices:
    if device['type'] == 'trezor':
        client = trezor.TrezorClient(device['path'])
        print(device['path'])

client.prompt_pin()

pin = input('enter pin: ')
print(repr(pin))

devices = commands.enumerate()
for device in devices:
    if device['type'] == 'trezor':
        print(device['path'])
        client = trezor.TrezorClient(device['path'])

print(client.send_pin(pin))


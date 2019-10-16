'''
copied from https://github.com/bitcoin-core/HWI/blob/master/contrib/pyinstaller-hooks/hook-hwilib.devices.py
'''
from hwilib.devices import __all__
hiddenimports = []
for d in __all__:
    hiddenimports.append('hwilib.devices.' + d)

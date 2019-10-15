'''
FIXME: do these with hwilib.devices.coldcard
- `real_file_upload` is the only thing that's missing for multisig registration
FIXME: neither one of these can specify a specific coldcard device ...
'''

### Multisig registration

from ckcc.cli import ColdcardDevice, real_file_upload, MAX_BLK_LEN, CCProtocolPacker
from io import BytesIO

multisig_header = \
"""Name: {name}
Policy: {m} of {n}
Derivation: {path}
Format: {format}

"""
multisig_key = "\n{fingerprint}: {xpub}"

def generate_multisig_file(wallet):
    name = wallet.name[:20]  # 20 character max

    format = 'P2WSH' if wallet.script_type == 'native' else 'P2WSH-P2SH'

    contents = multisig_header.format(name=name, m=wallet.m, n=wallet.n, 
            path=wallet.account_derivation_path(), format=format)
    for signer in wallet.signers:
        contents += multisig_key.format(fingerprint=signer.fingerprint,
                                        xpub=signer.xpub)

    return BytesIO(contents.encode())

def enroll(wallet):
    multisig_file = generate_multisig_file(wallet)

    force_serial = None
    dev = ColdcardDevice(sn=force_serial)

    file_len, sha = real_file_upload(multisig_file, MAX_BLK_LEN, dev=dev)

    payload = CCProtocolPacker.multisig_enroll(file_len, sha)
    dev.send_recv(payload)
    dev.close()

### Address display

from ckcc.cli import show_address, AF_P2WSH, AF_P2SH, AF_P2WSH_P2SH, a2b_hex, str_to_int_path

def display_multisig_address(redeem_script_hex, derivation_paths, segwit):
    script = a2b_hex(redeem_script_hex)

    min_signers = script[0] - 80
 
    if segwit:
        addr_fmt = AF_P2WSH
    else:
        addr_fmt = AF_P2WSH_P2SH

    xfp_paths = []
    for idx, xfp in enumerate(derivation_paths):
        assert '/' in xfp, 'Needs a XFP/path: ' + xfp
        xfp, p = xfp.split('/', 1)

        xfp_paths.append(str_to_int_path(xfp, p))
    
    dev = ColdcardDevice(sn=None)
    payload = CCProtocolPacker.show_p2sh_address(min_signers, xfp_paths, script, addr_fmt=addr_fmt)
    dev.send_recv(payload, timeout=None)
    dev.close()
    
def check_multisig(wallet):    
    xfp_xor = 0
    for signer in wallet.signers:
        xfp_bytes = bytes.fromhex(signer.fingerprint)
        xfp_int = int.from_bytes(xfp_bytes, 'little')
        xfp_xor ^= xfp_int

    dev = ColdcardDevice(sn=None)
    payload = CCProtocolPacker.multisig_check(wallet.m, wallet.n, xfp_xor)
    res = dev.send_recv(payload, timeout=None)
    dev.close()

    assert res < 2, 'Multisig wallet collision'
    return bool(res)

if __name__ == '__main__':
    raw_script = '52210221cbdd9396872a0995f3bec8f2d16ce2d68391e698ff64fab0e46e166262f2262102ce9cb384b6d4ba788490531aa513f5f5f052fd77c1ebdd3f8c9bf1a027699da721032eb8ad3f64cd5ab4673cd029b0e7f3624b425a1df2c4d9ec4c4a1c7ba516ae6153ae'
    fingerprints = ["5b98d98d/44'/1'/0'/0/73", "6bb3d403/44'/1'/0'/0/73", "7209ddfa/44'/1'/0'/0/73"]
    segwit = True
    display_multisig_address(raw_script, fingerprints, segwit)
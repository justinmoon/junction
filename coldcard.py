# FIXME: do this with hwilib.devices.coldcard
# `real_file_upload` is the only thing that's missing
from ckcc.cli import ColdcardDevice, real_file_upload, MAX_BLK_LEN, CCProtocolPacker
from io import BytesIO

multisig_header = \
"""Name: {name}
Policy: {m} of {n}
Derivation: {path}
Format: {format}

"""
multisig_key = "\n{fingerprint}: {xpub}"

def coldcard_multisig_file(wallet):
    name = wallet.name[:20]  # 20 character max
    contents = multisig_header.format(name=name, m=wallet.m, n=wallet.n, 
                                      path="m/44'/1'/0'", format='P2SH')
    for signer in wallet.signers:
        contents += multisig_key.format(fingerprint=signer['fingerprint'],
                                        xpub=signer['xpub'])

    return BytesIO(contents.encode())

def coldcard_enroll(wallet):
    multisig_file = coldcard_multisig_file(wallet)

    force_serial = None
    dev = ColdcardDevice(sn=force_serial)

    file_len, sha = real_file_upload(multisig_file, MAX_BLK_LEN, dev=dev)

    dev.send_recv(CCProtocolPacker.multisig_enroll(file_len, sha))

def handle_exception(exception, user=None):
    ''' prints the exception and most important the stacktrace '''
    app.logger.error("Unexpected error")
    app.logger.error("----START-TRACEBACK-----------------------------------------------------------------")
    app.logger.exception(exception)    # the exception instance
    app.logger.error("----END---TRACEBACK-----------------------------------------------------------------")

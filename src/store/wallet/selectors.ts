import { AppState } from '..';
import { Signer, isUnlockedDevice, Device, Wallet } from '../../types'
import { selectDevices } from '../device';

export function selectCandidateDevicesForActiveWallet(state: AppState) {
  // FIXME this check sucks
  const activeWallet = selectActiveWallet(state)
  if (!state.device.devices.data || !activeWallet) {
    return [];
  }
  const walletFingerprints = activeWallet.signers.map((signer: Signer) => signer.fingerprint);

  return state.device.devices.data.filter(device => {
    if (isUnlockedDevice(device) && walletFingerprints.includes(device.fingerprint)) {
      return false;
    }
    return true;
  });
}

export function selectUnregisteredSigners(state: AppState) {
  const activeWallet = selectActiveWallet(state)
  const devices = state.device.devices.data;
  if (!devices || !activeWallet) {
    return [];
  }
  const unregistered = []
  for (let signer of activeWallet.signers) {
    if (signer.type === 'coldcard') {
      unregistered.push(signer)
    }
  }
  return unregistered
}

// This is hard to use 
export function selectActiveWallet(state: AppState) {
  const { activeWalletName } = state.wallet;

  if (state.wallet.wallets.data !== null) {
    for (let wallet of state.wallet.wallets.data) {
      if (wallet.name === activeWalletName) {
        return wallet
      }
    }
  }
  return null
}

export function signedBySigner(signer: Signer, psbt: any) {
  for (let input of psbt.inputs) {
    let signed = false;
    for (let deriv of input.bip32_derivs) {
      const fingerprintMatch = deriv.master_fingerprint === signer.fingerprint;
      if (!input.partial_signatures) {
        return false;
      }
      const pubkeyMatch = deriv.pubkey in input.partial_signatures
      if (fingerprintMatch && pubkeyMatch) {
        signed = true
      }
    }
    // return false if any input is unsigned
    if (!signed) return false;
  }
  // if every input is signed, return true
  return true;
}

export function deviceAvailable(signer: Signer, devices: Device[]) {
  // look for a device with fingerprint matching signer's fingerprint
  for (let device of devices) {
    // FIXME: this check sucks
    if ('fingerprint' in device && device.fingerprint === signer.fingerprint) {
      return device
    }
  }
  return null;
}

export function signaturesRemaining(wallet: Wallet, psbt: any) {
  const partialSignatures = ('partial_signatures' in psbt.inputs[0]) 
    ? Object.keys(psbt.inputs[0].partial_signatures).length
    : 0;
  return Math.max(wallet.m - partialSignatures, 0)
}

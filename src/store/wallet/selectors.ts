import { AppState } from '..';
import { Signer, Device, isUnlockedDevice } from '../../types'

export function selectCandidateDevicesForActiveWallet(state: AppState) {
  // FIXME this check sucks
  if (!state.device.devices.data || !state.wallet.activeWallet) {
    return [];
  }
  const walletFingerprints = state.wallet.activeWallet.signers.map((signer: Signer) => signer.fingerprint);

  return state.device.devices.data.filter(device => {
    if (isUnlockedDevice(device) && walletFingerprints.includes(device.fingerprint)) {
      return false;
    }
    return true;
  });
}

// This is hard to use 
export function selectActiveWallet(state: AppState) {
  const { activeWallet } = state.wallet;
  // if (activeWallet === null) {
  //   throw Error('No active wallet');
  // }
  return activeWallet;
}
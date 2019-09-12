import { AppState } from '..';
import { Signer, Device } from '../../types'

export function selectCandidateDevicesForActiveWallet(state: AppState) {
  // FIXME this check sucks
  if (state.device.devices.data === null || state.wallet.activeWallet === null) {
    return [];
  }
  const walletFingerprints = state.wallet.activeWallet.signers.map((signer: Signer) => signer.fingerprint);
  return state.device.devices.data.reduce(
    (candidates: Device[], device: Device) => {
      console.log('device', device)
      if (device.fingerprint && !walletFingerprints.includes(device.fingerprint)) {
        candidates.push(device);
      }
      return candidates;
  }, [])
}

// This is hard to use 
export function selectActiveWallet(state: AppState) {
  const { activeWallet } = state.wallet;
  // if (activeWallet === null) {
  //   throw Error('No active wallet');
  // }
  return activeWallet;
}
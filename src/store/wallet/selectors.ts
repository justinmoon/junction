import { AppState } from '..';
import { Signer, isUnlockedDevice } from '../../types'

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


import { WalletActionTypes as T } from './types';
import { ThunkAction } from '../types';
import { Wallet, Device } from '../../types';
import api from '../../api';
import { selectActiveWallet } from './selectors';


export function getWallets(): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.GET_WALLETS });
    try {
      const wallets = await api.getWallets();
      const activeWallet = selectActiveWallet(getState())
      if (!activeWallet) {
        dispatch(changeWallet(wallets[0]));
      }
      dispatch({ type: T.GET_WALLETS_SUCCESS, payload: wallets });
    } catch(err) {
      dispatch({ type: T.GET_WALLETS_FAILURE, payload: err });
    }
  };
}

export function addSigner(device: Device): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.ADD_SIGNER });
    const state = getState()
    const activeWallet = selectActiveWallet(state)
    try {
      // FIXME
      if (activeWallet && 'fingerprint' in device && device.fingerprint !== undefined) {
        const wallets = await api.addSigner({
          wallet_name: activeWallet.name,
          signer_name: device.type,
          device_id: device.fingerprint,
        });
      }
      await dispatch(getWallets())
      dispatch({ type: T.ADD_SIGNER_SUCCESS });
    } catch(err) {
      dispatch({ type: T.ADD_SIGNER_FAILURE, payload: err });
    }
  };
}

export function changeWallet(wallet: Wallet) {
  return {
    type: T.CHANGE_WALLET,
    payload: wallet.name,
  };
}

import { WalletActionTypes as T } from './types';
import { ThunkAction } from '../types';
import { Wallet, UnlockedDevice } from '../../types';
import api from '../../api';
import { selectActiveWallet } from './selectors';
import { notNull } from '..';

export function getWallets(): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.GET_WALLETS });
    try {
      const wallets = await api.getWallets();
      const activeWallet = selectActiveWallet(getState())
      if (!activeWallet) {
        // FIXME: use the most recently updated wallet ...
        dispatch(changeWallet(wallets[0]));
      }
      dispatch({ type: T.GET_WALLETS_SUCCESS, payload: wallets });
    } catch(err) {
      dispatch({ type: T.GET_WALLETS_FAILURE, payload: err });
    }
  };
}

export function addSigner(device: UnlockedDevice): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.ADD_SIGNER, device });
    const state = getState()
    const activeWallet = notNull(selectActiveWallet(state))
    try {
      await api.addSigner({
        wallet_name: activeWallet.name,
        signer_name: device.type,
        device_id: device.fingerprint,
      });
      await dispatch(getWallets())
      dispatch({ type: T.ADD_SIGNER_SUCCESS });
    } catch(err) {
      dispatch({ type: T.ADD_SIGNER_FAILURE, payload: err });
    }
  };
}

export function signPSBT(device: UnlockedDevice, index: number): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.SIGN_PSBT, device });
    try {
      const activeWallet = notNull(selectActiveWallet(getState()))
      const device_id = device.fingerprint
      await api.signPSBT({ wallet_name: activeWallet.name, device_id, index });
      await dispatch(getWallets())
      dispatch({ type: T.SIGN_PSBT_SUCCESS })
    } catch(error) {
      dispatch({ type: T.SIGN_PSBT_FAILURE, error })
    }
  }
}

export function changeWallet(wallet: Wallet) {
  return {
    type: T.CHANGE_WALLET,
    payload: wallet.name,
  };
}


export function broadcastTransaction(index: number): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.BROADCAST_TRANSACTION });
    try {
      const activeWallet = notNull(selectActiveWallet(getState()))
      await api.broadcastTransaction({ wallet_name: activeWallet.name, index });
      await dispatch(getWallets())
      dispatch({ type: T.BROADCAST_TRANSACTION_SUCCESS })
    } catch(error) {
      dispatch({ type: T.BROADCAST_TRANSACTION_FAILURE, error })
    }
  }
}
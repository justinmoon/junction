import { WalletActionTypes as T } from './types';
import { ThunkAction } from '../types';
import { Wallet, UnlockedDevice, Signer } from '../../types';
import api from '../../api';
import { selectActiveWallet } from './selectors';
import { notNull } from '..';
import { toggleConnectRPCModal } from '../modal'

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

export function addSigner(device: UnlockedDevice, nickname: string): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.ADD_SIGNER, device });
    const state = getState()
    const activeWallet = notNull(selectActiveWallet(state))
    try {
      await api.addSigner({
        wallet_name: activeWallet.name,
        signer_name: nickname,
        device_id: device.fingerprint,
      });
      await dispatch(getWallets())
      dispatch({ type: T.ADD_SIGNER_SUCCESS });
    } catch(error) {
      dispatch({ type: T.ADD_SIGNER_FAILURE, error });
    }
  };
}

export function registerSigner(signer: Signer): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.REGISTER_SIGNER, signer });
    const state = getState()
    const activeWallet = notNull(selectActiveWallet(state))
    try {
      await api.registerSigner({
        wallet_name: activeWallet.name,
        device_id: signer.fingerprint,
      });
      await dispatch(getWallets())
      dispatch({ type: T.REGISTER_SIGNER_SUCCESS });
    } catch(error) {
      dispatch({ type: T.REGISTER_SIGNER_FAILURE, error });
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

// export function changeWallet(wallet: Wallet): ThunkAction {
//   // FIXME: doesn't need to be async ...
//   return async (dispatch, getState) => {
//     await dispatch({ type: T.CHANGE_WALLET, payload: wallet.name });
//     const activeWallet = notNull(selectActiveWallet(getState()))
//     const hasRpcError = !!activeWallet.node.rpc_error
//     const notSynced = activeWallet.synced === false
//     const showModal = hasRpcError || notSynced
//     if (showModal) {
//       dispatch(toggleConnectRPCModal())
//     }
//   }
// }

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
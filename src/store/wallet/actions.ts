import { WalletActionTypes as T } from './types';
import { ThunkAction } from '../types';
import { Wallet } from '../../types';
import api from '../../api';

export function getWallets(): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.GET_WALLETS });
    try {
      const wallets = await api.getWallets();
      if (!getState().wallet.activeWallet) {
        dispatch(changeWallet(wallets[0]));
      }
      dispatch({ type: T.GET_WALLETS_SUCCESS, payload: wallets });
    } catch(err) {
      dispatch({ type: T.GET_WALLETS_FAILURE, payload: err });
    }
  };
}

export function changeWallet(wallet: Wallet) {
  return {
    type: T.CHANGE_WALLET,
    payload: wallet,
  };
}

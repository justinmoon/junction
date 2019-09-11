import { AnyAction } from 'redux';
import { Wallet } from '../../types';
import { Loadable, DEFAULT_LOADABLE, handleLoadable } from '../util';
import { WalletActionTypes as T } from './types';

export interface WalletState {
  wallets: Loadable<Wallet[]>;
  activeWallet: Wallet | null;
}

export const INITIAL_STATE: WalletState = {
  wallets: { ...DEFAULT_LOADABLE },
  activeWallet: null,
};

export function walletReducer(
  state: WalletState = INITIAL_STATE,
  action: AnyAction,
): WalletState {
  switch(action.type) {
    case T.GET_WALLETS:
    case T.GET_WALLETS_SUCCESS:
    case T.GET_WALLETS_FAILURE:
      return {
        ...state,
        wallets: handleLoadable(state.wallets, action),
      };

    case T.CHANGE_WALLET:
      return {
        ...state,
        activeWallet: action.payload,
      };
  }
  return state;
}

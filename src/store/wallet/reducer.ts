import { AnyAction } from 'redux';
import { Wallet, Device, UnlockedDevice } from '../../types';
import { Loadable, DEFAULT_LOADABLE, handleLoadable } from '../util';
import { WalletActionTypes as T } from './types';

export interface WalletState {
  wallets: Loadable<Wallet[]>;
  activeWalletName: string | null;
  addSigner: {
    isSubmitting: boolean;
    device: Device | null;
  }
  signPSBT: {
    device: UnlockedDevice | null;
    error: Error | null;
  }
  broadcastTransaction: {
    pending: boolean;
    error: Error | null;
  }
}

export const INITIAL_STATE: WalletState = {
  wallets: { ...DEFAULT_LOADABLE },
  activeWalletName: null,
  addSigner: {
    isSubmitting: false,
    device: null,
  },
  signPSBT: {
    device: null,
    error: null
  },
  broadcastTransaction: {
    pending: false,
    error: null,
  },
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
        activeWalletName: action.payload,
      };
    
    case T.SIGN_PSBT:
      return {
        ...state,
        signPSBT: {
          device: action.device,
          error: null,
        }
      }

    case T.SIGN_PSBT_SUCCESS:
        return {
          ...state,
          signPSBT: INITIAL_STATE.signPSBT,
        }

    case T.SIGN_PSBT_FAILURE:
        return {
          ...state,
          signPSBT: {
            device: null,
            error: action.error,
          }
        }

    case T.BROADCAST_TRANSACTION:
        return {
          ...state,
          broadcastTransaction: {
            pending: true,
            error: null,
          }
        }
      
    case T.BROADCAST_TRANSACTION_SUCCESS:
        return {
          ...state,
          broadcastTransaction: INITIAL_STATE.broadcastTransaction,
        }

    case T.BROADCAST_TRANSACTION_FAILURE:
        return {
          ...state,
          broadcastTransaction: {
            pending: false,
            error: action.error,
          }
        }
  }
  return state;
}

import { WalletActionTypes as T } from './types';
import { ThunkAction } from '../types';
import { Wallet, DeviceType } from '../../types';
import { sleep } from '../../util';

export function getWallets(): ThunkAction {
  return async (dispatch) => {
    dispatch({ type: T.GET_WALLETS });

    await sleep(500);

    const wallets = [{
      name: 'Cold storage',
      m: 2,
      n: 3,
      signers: [{
        name: 'Ledger',
        type: DeviceType.ledger,
        fingerprint: '123',
        xpub: '456',
      }],
    }, {
      name: 'Family wallet',
      m: 3,
      n: 5,
      signers: [{
        name: 'Me',
        type: DeviceType.ledger,
        fingerprint: '123',
        xpub: '456',
      }, {
        name: 'Mom',
        type: DeviceType.ledger,
        fingerprint: 'xyz',
        xpub: '789',
      }, {
        name: 'Dad',
        type: DeviceType.ledger,
        fingerprint: 'abc',
        xpub: '000',
      }],
    }];
    dispatch({ type: T.GET_WALLETS_SUCCESS, payload: wallets });
    dispatch(changeWallet(wallets[0]));
  };
}

export function changeWallet(wallet: Wallet) {
  return {
    type: T.CHANGE_WALLET,
    payload: wallet,
  };
}

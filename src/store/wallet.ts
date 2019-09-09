import { observable, action, runInAction } from 'mobx';
import { Wallet, DeviceType } from '../types';
import { sleep } from '../util';

export class WalletStore {
  @observable wallets: Wallet[] = [];
  @observable activeWallet: Wallet | null = null;

  // TODO: Actually get wallets from python backend
  @action
  async getWallets() {
    await sleep(300);
    runInAction(() => {
      this.wallets = [{
        name: 'Cold storage',
        m: 2,
        n: 3,
        signers: [{
          name: 'Ledger',
          type: DeviceType.ledger,
          fingerprint: '123',
          xpub: '456',
        }],
      }];
      this.changeWallet(this.wallets[0]);
    });
  }

  @action
  changeWallet(wallet: Wallet) {
    this.activeWallet = wallet;
  }
}
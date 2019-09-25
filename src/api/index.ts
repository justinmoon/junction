import { stringify } from 'query-string';
import * as T from '../api/types';
import { Device } from '../types';
import { Settings } from '../store/settings';
export * from '../api/types';

class API {
  url: string;

  constructor(url: string) {
    this.url = url;
  }

  // Public methods
  getDevices() {
    return this.request<Device[]>('GET', '/devices');
  }

  getSettings() {
    return this.request<Settings>('GET', '/settings');
  }

  updateSettings(settings: Settings) {
    delete settings.rpc.error;
    return this.request<Settings>('PUT', '/settings', settings);
  }

  getWallets() {
    return this.request<any>('GET', '/wallets');
  }

  createWallet(args: T.CreateWalletArguments) {
    return this.request<any>('POST', '/wallets', args);
  }

  addSigner(args: T.AddSignerArguments) {
    return this.request<any>('POST', '/signers', args);
  }

  promptPin() {
    return this.request<any>('POST', '/prompt')
  }

  enterPin(args: T.EnterPinArguments) {
    return this.request<any>('POST', '/unlock', args)
  }

  deletePrompt() {
    return this.request<any>('DELETE', '/prompt',)
  }

  createPSBT(args: T.CreatePSBTArguments) {
    return this.request<any>('POST', '/psbt', args);
  }

  signPSBT(args: T.SignPSBTArguments) {
    return this.request<any>('POST', '/sign', args);
  }

  broadcastTransaction(args: T.BroadcastTransactionArguments) {
    return this.request<any>('POST', '/broadcast', args);
  }

  // Internal fetch function
  protected request<R extends object>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    path: string,
    args?: object,
  ): Promise<R> {
    let body = null;
    let query = '';
    const headers = new Headers();
    headers.append('Accept', 'application/json');

    if (method === 'POST' || method === 'PUT') {
      body = JSON.stringify(args);
      headers.append('Content-Type', 'application/json');
    }
    else if (args !== undefined) {
      // TS Still thinks it might be undefined(?)
      query = `?${stringify(args as any)}`;
    }

    return fetch(this.url + path + query, {
      method,
      headers,
      body,
    })
    .then(async res => {
      if (!res.ok) {
        let errMsg;
        try {
          const errBody = await res.json();
          if (!errBody.error) throw new Error();
          errMsg = errBody.error;
        } catch(err) {
          throw new Error(`${res.status}: ${res.statusText}`);
        }
        throw new Error(errMsg);
      }
      return res.json();
    })
    .then(res => res as R)
    .catch((err) => {
      console.error(`API error calling ${method} ${path}`, err);
      throw err;
    });
  }
}

// TODO: Environment variable?
export default new API('http://localhost:37128');

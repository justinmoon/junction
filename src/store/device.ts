import { observable, action, runInAction } from 'mobx';
import { sleep } from '../util';
import { Device, DeviceType } from '../types';

export class DeviceStore {
  @observable devices: Device[] = [];

  // TODO: Actually get devices from python backend
  @action
  async getDevices() {
    await sleep(500);
    runInAction(() => {
      this.devices = [{
        name: 'Ledger',
        type: DeviceType.ledger,
        fingerprint: '123',
      }];
    });
  }
}

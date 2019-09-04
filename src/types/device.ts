export enum DeviceType {
  ledger = 'ledger',
}

export interface Device {
  name: string;
  type: DeviceType;
  fingerprint: string;
}
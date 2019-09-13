export enum DeviceType {
  ledger = 'ledger',
  trezor = 'trezor',
  coldcard = 'coldcard',
}

export interface Device {
  name: string;
  type: DeviceType;
  fingerprint: string;
  needs_pin_sent: boolean;
  needs_passphrase_sent: boolean;
}

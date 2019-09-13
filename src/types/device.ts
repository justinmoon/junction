export enum DeviceType {
  ledger = 'ledger',
  trezor = 'trezor',
  coldcard = 'coldcard',
}

// FIXME: some of these are null at times
// but I don't really want typescript yelling at me all the time ...
export interface Device {
  name: string;
  type: DeviceType;
  fingerprint: string;
  path: string;
  needs_pin_sent: boolean;
  needs_passphrase_sent: boolean;
}

export enum DeviceType {
  ledger = 'ledger',
  trezor = 'trezor',
  coldcard = 'coldcard',
}

// FIXME: some of these are null at times
// but I don't really want typescript yelling at me all the time ...
export interface BaseDevice {
  path: string;
  type: DeviceType;
}

export interface UnlockedDevice extends BaseDevice {
  fingerprint: string;
  needs_pin_sent: false;
  needs_passphrase_sent: false;
  error: undefined;
}

export interface LockedDevice extends BaseDevice {
  error: string | undefined;
  fingerprint: undefined;
  needs_pin_sent: true;
  needs_passphrase_sent: true;
}

export interface ErrorDevice extends BaseDevice {
  needs_pin_sent: false;
  needs_passphrase_sent: false;
  code: number;
  error: string;
}

export type Device = UnlockedDevice | LockedDevice | ErrorDevice;

export function isUnlockedDevice(device: Device): device is UnlockedDevice {
  return !!(device as UnlockedDevice).fingerprint;
}

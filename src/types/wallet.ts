import { DeviceType } from './device';

export interface Signer {
  name: string;
  type: DeviceType;
  fingerprint: string;
  xpub: string;
}

// Aligns with MultisigWallet in junction.py
export interface Wallet {
  name: string;
  m: number;
  n: number;
  signers: Signer[];
  balances: any;  // FIXME
  ready: boolean;
  psbt: any;      // FIXME
  signatures_remaining: number;
}
import { DeviceType } from './device';

export enum Network {
  mainnet = 'mainnet',
  testnet = 'testnet',
  regtest = 'regtest',
}

export enum WalletType {
  single = 'single',
  multi = 'multi',
}

export enum ScriptType {
  native = 'native',
  wrapped = 'wrapped',
}

export interface Node {
  host: string;
  port: string;
  user: string;
  password: string;
  wallet_name: string;
  network: Network;
  rpc_error: string;
}

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
  psbts: any;      // FIXME
  history: any;
  coins: any;
  node: Node;
  wallet_type: WalletType;
  script_type: ScriptType;
  network: string;
  synced: boolean;
}
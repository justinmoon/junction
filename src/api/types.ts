import { SendFormOutputs } from '../types/tx';

export interface CreateWalletArguments {
  name: string;
  n: number;
  m: number;
}

export interface CreatePSBTArguments {
  wallet_name: string;
  outputs: SendFormOutputs;
}
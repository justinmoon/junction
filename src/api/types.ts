export interface CreateWalletArguments {
  name: string;
  n: number;
  m: number;
}

export interface CreatePSBTOutput {
  address: string | undefined;
  btc: number | undefined;
}

export interface CreatePSBTArguments {
  wallet_name: string;
  outputs: CreatePSBTOutput[];
}
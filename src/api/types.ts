export interface CreateWalletArguments {
  name: string;
  n: number;
  m: number;
}

export interface CreatePSBTOutput {
  address: string | undefined;
  btc: number | undefined;
}

export interface CreatePSBTOutputs extends Array<CreatePSBTOutput>{}

export interface CreatePSBTArguments {
  wallet_name: string;
  outputs: CreatePSBTOutputs;
}
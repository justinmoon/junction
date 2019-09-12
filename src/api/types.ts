export interface CreateWalletArguments {
  name: string;
  n: number;
  m: number;
}

export interface AddSignerArguments {
  wallet_name: string;
  signer_name: string;
  device_id: string;
}
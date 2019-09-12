export interface CreateWalletArguments {
  name: string;
  n: number;
  m: number;
}

export interface AddSignerArguments {
  walet_name: string;
  signer_name: string;
  id: string;
}
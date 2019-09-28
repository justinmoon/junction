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

export interface EnterPinArguments {
  pin: string;
}

export interface CreatePSBTOutput {
  address: string | undefined;
  btc: number | undefined;
}

export interface CreatePSBTArguments {
  wallet_name: string;
  outputs: CreatePSBTOutput[];
}

export interface SignPSBTArguments {
  wallet_name: string;
  device_id: string;
}

export interface BroadcastTransactionArguments {
  wallet_name: string;
}

export interface GenerateAddressArguments {
  wallet_name: string;
}
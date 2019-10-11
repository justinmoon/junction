export interface CreateWalletArguments {
  name: string;
  n: number;
  m: number;
  network: string;
  node: {
    user: string;
    password: string;
    host: string;
    port: string;
  }
}

export interface AddSignerArguments {
  wallet_name: string;
  signer_name: string;
  device_id: string;
}

export interface RegisterSignerArguments {
  wallet_name: string;
  device_id: string;
}

export interface EnterPinArguments {
  pin: string;
}

export interface PromptPinArguments {
  wallet_name: string;
}

export interface CreatePSBTOutput {
  address: string | undefined;
  btc: number | undefined;
  subtract_fees: boolean;
}

export interface CreatePSBTArguments {
  wallet_name: string;
  outputs: CreatePSBTOutput[];
}

export interface SignPSBTArguments {
  wallet_name: string;
  device_id: string;
  index: number;
}

export interface BroadcastTransactionArguments {
  wallet_name: string;
  index: number;
}

export interface GenerateAddressArguments {
  wallet_name: string;
}

export interface DisplayAddressArguments {
  wallet_name: string;
  device_id: string;
  address: string;
}
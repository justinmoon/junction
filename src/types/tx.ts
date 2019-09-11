export interface SendFormOutput {
  address: string | undefined;
  btc: number | undefined;
}

export interface SendFormOutputs extends Array<SendFormOutput>{}
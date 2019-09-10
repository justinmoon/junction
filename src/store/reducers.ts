import { combineReducers } from 'redux';
import { DeviceState, deviceReducer } from './device';
import { WalletState, walletReducer } from './wallet';

export interface AppState {
  device: DeviceState;
  wallet: WalletState;
}

export const rootReducer = combineReducers<AppState>({
  device: deviceReducer,
  wallet: walletReducer,
});

import { combineReducers } from 'redux';
import { DeviceState, deviceReducer } from './device';
import { WalletState, walletReducer } from './wallet';
import { SettingsState, settingsReducer } from './settings';

export interface AppState {
  device: DeviceState;
  wallet: WalletState;
  settings: SettingsState;
}

export const rootReducer = combineReducers<AppState>({
  device: deviceReducer,
  wallet: walletReducer,
  settings: settingsReducer,
});

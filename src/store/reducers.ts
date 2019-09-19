import { combineReducers } from 'redux';
import { DeviceState, deviceReducer } from './device';
import { WalletState, walletReducer } from './wallet';
import { SettingsState, settingsReducer } from './settings';
import { ModalState, modalReducer } from './modal';

export interface AppState {
  device: DeviceState;
  wallet: WalletState;
  settings: SettingsState;
  modal: ModalState;
}

export const rootReducer = combineReducers<AppState>({
  device: deviceReducer,
  wallet: walletReducer,
  settings: settingsReducer,
  modal: modalReducer,
});

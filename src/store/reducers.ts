import { combineReducers } from 'redux';
import { DeviceState, deviceReducer } from './device';
import { WalletState, walletReducer } from './wallet';
import { SettingsState, settingsReducer } from './settings';
import { ModalState, modalReducer } from './modal';
import { BootstrapState, bootstrapReducer } from './bootstrap';

export interface AppState {
  device: DeviceState;
  wallet: WalletState;
  settings: SettingsState;
  modal: ModalState;
  bootstrap: BootstrapState;
}

export const rootReducer = combineReducers<AppState>({
  device: deviceReducer,
  wallet: walletReducer,
  settings: settingsReducer,
  modal: modalReducer,
  bootstrap: bootstrapReducer,
});
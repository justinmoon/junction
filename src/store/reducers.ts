import { combineReducers } from 'redux';
import { DeviceState, deviceReducer } from './device';
import { ModalState, modalReducer } from './modal';
import { BootstrapState, bootstrapReducer } from './bootstrap';
import { NodeState, nodeReducer } from './node';


// FIXME: can't import both these from ./wallet
import { WalletState } from './wallet';
import { walletReducer } from './wallet/reducer';

export interface AppState {
  device: DeviceState;
  wallet: WalletState;
  node: NodeState;
  modal: ModalState;
  bootstrap: BootstrapState;
}

export const rootReducer = combineReducers<AppState>({
  device: deviceReducer,
  wallet: walletReducer,
  modal: modalReducer,
  node: nodeReducer,
  bootstrap: bootstrapReducer,
});
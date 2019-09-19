import { AnyAction } from 'redux';
import { Device } from '../../types';
import { Loadable, DEFAULT_LOADABLE, handleLoadable } from '../util';
import { ModalActionTypes as T } from './types';

// FIXME: "isOpen" would be better than "open"
export interface ModalState {
  deviceInstructions: {
    device: Device | null;
    open: boolean;
  };
  deviceUnlock: {
    device: Device | null;
    open: boolean;
  }
}

export const INITIAL_STATE: ModalState = {
  deviceInstructions: {
    device: null,
    open: false,
  },
  deviceUnlock: {
    device: null,
    open: false,
  }
};

export function modalReducer(
  state: ModalState = INITIAL_STATE,
  action: AnyAction,
): ModalState {
  switch(action.type) {
    case T.DEVICE_INSTRUCTIONS_TOGGLE:
      return {
        ...state,
        deviceInstructions: {
          open: !state.deviceInstructions.open,
          device: state.deviceInstructions.device,
        }
      }
    // FIXME: ideally this would require a device attr if showing,
    // would set device attr to null if hiding.
    case T.DEVICE_UNLOCK_TOGGLE:
      return {
        ...state,
        deviceUnlock: {
          open: !state.deviceUnlock.open,
          device: state.deviceUnlock.device,
        }
      }
    case T.DEVICE_UNLOCK_SET_DEVICE:
      return {
        ...state,
        deviceUnlock: {
          open: state.deviceUnlock.open,
          device: action.device,
        }
      }
  }
  return state;
}
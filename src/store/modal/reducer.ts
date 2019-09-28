import { AnyAction } from 'redux';
import { DeviceType } from '../../types';
import { ModalActionTypes as T } from './types';

// FIXME: "isOpen" would be better than "open"
export interface ModalState {
  deviceInstructions: {
    deviceType: DeviceType | null;
    open: boolean;
  };
  deviceUnlock: {
    open: boolean;
  }
}

export const INITIAL_STATE: ModalState = {
  deviceInstructions: {
    deviceType: null,
    open: false,
  },
  deviceUnlock: {
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
          deviceType: action.deviceType,
        }
      }
    case T.DEVICE_UNLOCK_TOGGLE:
      return {
        ...state,
        deviceUnlock: {
          open: !state.deviceUnlock.open,
        }
      }
    case T.DEVICE_UNLOCK_SET_DEVICE:
      return {
        ...state,
        deviceUnlock: {
          open: state.deviceUnlock.open,
        }
      }
  }
  return state;
}
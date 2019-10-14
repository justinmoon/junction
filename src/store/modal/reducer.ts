import { AnyAction } from 'redux';
import { DeviceType } from '../../types';
import { ModalActionTypes as T, ModalNames } from './types';

// FIXME: "isOpen" would be better than "open"
export interface ModalState {
  deviceInstructions: {
    deviceType: DeviceType | null;
    open: boolean;
  };
  deviceUnlock: {
    open: boolean;
  };
  displayAddress: {
    address: string | null;
    open: boolean;
  };
  connectRPC: {
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
  },
  displayAddress: {
    open: false,
    address: null,
  },
  connectRPC: {
    open: false,
  },
};

export interface ModalAction extends AnyAction {
  // Make sure modalName is kosher
  modalName: ModalNames,
}

export function modalReducer(
  state: ModalState = INITIAL_STATE,
  action: ModalAction,
): ModalState {
  switch(action.type) {
    case T.TOGGLE:
     return {
       ...state,
       [action.modalName]: {
         open: !state[action.modalName].open,
         ...action.data,
       }
     }
  }
  return state;
}
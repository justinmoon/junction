import { AnyAction } from 'redux';
import { Device } from '../../types';
import { Loadable, DEFAULT_LOADABLE, handleLoadable } from '../util';
import { DeviceActionTypes as T } from './types';

export interface DeviceState {
  devices: Loadable<Device[]>;
}

export const INITIAL_STATE: DeviceState = {
  devices: { ...DEFAULT_LOADABLE },
};

export function deviceReducer(
  state: DeviceState = INITIAL_STATE,
  action: AnyAction,
): DeviceState {
  switch(action.type) {
    case T.GET_DEVICES:
    case T.GET_DEVICES_SUCCESS:
    case T.GET_DEVICES_FAILURE:
      return {
        ...state,
        devices: handleLoadable(state.devices, action),
      };
  }
  return state;
}
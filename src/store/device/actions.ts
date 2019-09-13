import { DeviceActionTypes as T } from './types';
import { ThunkAction } from '../types';
import { sleep } from '../../util';
import api from '../../api';

export function getDevices(): ThunkAction {
  return async (dispatch) => {
    dispatch({ type: T.GET_DEVICES });
    try {
      const devices = await api.getDevices();
      dispatch({ type: T.GET_DEVICES_SUCCESS, payload: devices });
    } catch(err) {
      dispatch({ type: T.GET_DEVICES_FAILURE, payload: err });
    }
  };
}

export function startDeviceScan(): ThunkAction {
  return async (dispatch, getState) => {
    dispatch({ type: T.SCAN_DEVICES_START });
    while (getState().device.isScanning) {
      await dispatch(getDevices());
      await sleep(3000);
    }
  };
}

export function stopDeviceScan() {
  return { type: T.SCAN_DEVICES_STOP };
}

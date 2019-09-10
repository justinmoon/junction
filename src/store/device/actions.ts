import { DeviceActionTypes as T } from './types';
import { ThunkAction } from '../types';
import { DeviceType } from '../../types';
import { sleep } from '../../util';

export function getDevices(): ThunkAction {
  return async (dispatch) => {
    dispatch({ type: T.GET_DEVICES });
    await sleep(500);
    dispatch({
      type: T.GET_DEVICES_SUCCESS,
      payload: [{
        name: 'Ledger',
        type: DeviceType.ledger,
        fingerprint: '123',
      }],
    })
  };
}

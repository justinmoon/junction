import { BootstrapActionTypes as T } from './types';
import { ThunkAction } from '../types';

import { getWallets } from '../wallet'
import { getDevices } from '../device'
import { getSettings } from '../settings'

export function bootstrap(): ThunkAction {
  return async (dispatch) => {
    dispatch({ type: T.BOOTSTRAP})
    try { 
      await dispatch(getDevices())
      await dispatch(getWallets())
      await dispatch(getSettings())
      dispatch({ type: T.BOOTSTRAP_SUCCESS })
    } catch(error) {
      dispatch({ type: T.BOOTSTRAP_SUCCESS, error })
    }
  }
}
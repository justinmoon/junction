import { BootstrapActionTypes as T } from './types';
import { ThunkAction } from '../types';

import { getWallets } from '../wallet'
import { getDevices } from '../device'
import { getNodes } from '../node'


export function bootstrap(): ThunkAction {
  return async (dispatch) => {
    dispatch({ type: T.BOOTSTRAP})
    try { 
      await dispatch(getDevices())
      await dispatch(getWallets())
      await dispatch(getNodes())
      dispatch({ type: T.BOOTSTRAP_SUCCESS })
    } catch(error) {
      dispatch({ type: T.BOOTSTRAP_SUCCESS, error })
    }
  }
}
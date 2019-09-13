import { SettingsActionTypes as T } from './types';
import { ThunkAction } from '../types';
import api from '../../api';
import { Settings } from './reducer';

export function getSettings(): ThunkAction {
  return async (dispatch) => {
    dispatch({ type: T.GET_SETTINGS });
    try {
      const devices = await api.getSettings();
      dispatch({ type: T.GET_SETTINGS_SUCCESS, payload: devices });
    } catch(err) {
      dispatch({ type: T.GET_SETTINGS_FAILURE, payload: err });
    }
  };
}

export function updateSettings(settings: Settings): ThunkAction {
  return async (dispatch) => {
    dispatch({ type: T.UPDATE_SETTINGS });
    try {
      const devices = await api.updateSettings(settings);
      dispatch({ type: T.UPDATE_SETTINGS_SUCCESS, payload: devices });
    } catch(err) {
      dispatch({ type: T.UPDATE_SETTINGS_FAILURE, payload: err });
    }
  };
}
import { AnyAction } from 'redux';
import { SettingsActionTypes as T } from './types';
import { Loadable, DEFAULT_LOADABLE, handleLoadable } from '../util';

export interface Settings {
  rpc: {
    user: string;
    password: string;
    host: string;
    port: string;
    error?: string;
  };
};

export type SettingsState = Loadable<Settings>;

export const INITIAL_STATE: SettingsState = { ...DEFAULT_LOADABLE };

export function settingsReducer(
  state: SettingsState = INITIAL_STATE,
  action: AnyAction,
): SettingsState {
  switch(action.type) {
    case T.GET_SETTINGS:
    case T.GET_SETTINGS_SUCCESS:
    case T.GET_SETTINGS_FAILURE:
    case T.UPDATE_SETTINGS:
    case T.UPDATE_SETTINGS_SUCCESS:
    case T.UPDATE_SETTINGS_FAILURE:
      return handleLoadable(state, action);
  }
  return state;
}

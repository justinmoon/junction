import { AnyAction } from 'redux';
import { BootstrapActionTypes as T } from './types';

export interface BootstrapState {
  ready: boolean,
  error: Error | null,
}

export const INITIAL_STATE: BootstrapState = {
  ready: false,
  error: null
};

export function bootstrapReducer(
  state: BootstrapState = INITIAL_STATE,
  action: AnyAction,
): BootstrapState {
  switch(action.type) {
    case T.BOOTSTRAP:
      return {
        ready: false,
        error: null,
      };
    case T.BOOTSTRAP_SUCCESS:
      return {
        ready: true,
        error: null,
      };
    case T.BOOTSTRAP_FAILURE:
      return {
        ready: false,
        error: action.error,
      }
  }
  return state;
}
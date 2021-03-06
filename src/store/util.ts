import { AnyAction } from 'redux';
import { ThunkAction } from './types';

// Reusable loadable type for data that needs to be fetched
export interface Loadable<T> {
  data: T | null;
  hasLoaded: boolean;
  isLoading: boolean;
  error: Error | null;
}

export const DEFAULT_LOADABLE: Loadable<any> = {
  data: null,
  hasLoaded: false,
  isLoading: false,
  error: null,
};

export const loadableLoading = (l: Loadable<any>): Loadable<any> => ({
  ...l,
  isLoading: true,
});

export const loadableSuccess = <T>(l: Loadable<T>, data: T): Loadable<T> => ({
  ...l,
  data,
  error: null,
  isLoading: false,
  hasLoaded: true,
});

export const loadableFailure = (l: Loadable<any>, error: Error): Loadable<any> => ({
  ...l,
  error,
  isLoading: false,
  hasLoaded: false,
});

export const handleLoadable = <T>(l: Loadable<T>, action: AnyAction): Loadable<T> => {
  if (action.type.includes('SUCCESS')) {
    return loadableSuccess(l, action.payload);
  } else if (action.type.includes('FAILURE')) {
    return loadableFailure(l, action.payload);
  } else {
    return loadableLoading(l);
  }
};

export function loadAction(func: any, start: string, success: string, failure: string): ThunkAction {
  return async (dispatch) => {
    dispatch({ type: start });
    try {
      const payload = await func();
      dispatch({ type: success, payload });
    } catch(err) {
      dispatch({ type: failure, payload: err });
    }
  };
}
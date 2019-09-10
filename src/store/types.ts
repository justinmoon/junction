import {
  ThunkAction as RTThunkAction,
  ThunkDispatch as RTThunkDispatch,
} from 'redux-thunk';
import { AppState } from './reducers';
import { AnyAction } from 'redux';

// Set up some nice & simple defaults for Thunk's overly verbose types
export type ThunkAction = RTThunkAction<any, AppState, undefined, AnyAction>;
export type ThunkDispatch = RTThunkDispatch<AppState, undefined, AnyAction>;

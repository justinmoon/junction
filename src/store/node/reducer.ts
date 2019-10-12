import { AnyAction } from 'redux';
import { Loadable, DEFAULT_LOADABLE, handleLoadable } from '../util';
import { NodeActionTypes as T } from './types';

export interface Nodes {
  bitcoin: any[];    // FIXME
  lightning: any[];  // FIXME
};

export type NodeState = Loadable<Nodes>;

export const INITIAL_STATE: NodeState = { ...DEFAULT_LOADABLE };

export function nodeReducer(
  state: NodeState = INITIAL_STATE,
  action: AnyAction,
): NodeState {
  switch(action.type) {
    case T.GET_NODES:
    case T.GET_NODES_SUCCESS:
    case T.GET_NODES_FAILURE:
      return handleLoadable(state, action);
  }
  return state;
}

import { SettingsActionTypes as T } from './types';
import api from '../../api';
import { loadAction } from '../util';

export function getNodes() {
  // FIXME: getNodes loses track of "this" without arrow function ...
  return loadAction(() => api.getNodes(), T.GET_NODES, T.GET_NODES_SUCCESS, T.GET_NODES_FAILURE)
}
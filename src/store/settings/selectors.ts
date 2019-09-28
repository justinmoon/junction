import { AppState } from "../reducers";

export const validSettingsSelector = (state: AppState) => {
  const data = state.settings.data
  return !!data && !data.rpc.error
}
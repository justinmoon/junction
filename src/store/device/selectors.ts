import { AppState } from '..';

export function selectDevices(state: AppState) {
  const devices = state.device.devices.data;
  if (devices === null) {
    throw Error('Device state is null')
  }
  return devices
}
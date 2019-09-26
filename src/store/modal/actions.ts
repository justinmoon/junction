import { ModalActionTypes as T } from './types';
import { DeviceType } from '../../types';
import api from '../../api'

export function toggleDeviceInstructionsModal(deviceType?: DeviceType) {
  return { type: T.DEVICE_INSTRUCTIONS_TOGGLE, deviceType }
}

export function toggleDeviceUnlockModal() {
  return async (dispatch: any, getState: any) => {
    const state = getState()
    const { open } = state.modal.deviceUnlock
    if (open) {
      await api.deletePrompt()
    } else {
      // FIXME: throw if it's not there
      await api.promptPin()
    }
    dispatch({ type: T.DEVICE_UNLOCK_TOGGLE })
  }
}
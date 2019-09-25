import { ModalActionTypes as T } from './types';
import { DeviceType } from '../../types';
import api from '../../api'

// TODO: this should should hit API and prompt pin if necessary ...
// this could hit all devices with needs_pin_entry ... 
// if showing, require a "device" attribute
// if hiding, remove device attribute

// we need API method to "promptAllDevices"
export function toggleDeviceInstructionsModal(deviceType?: DeviceType) {
  return { type: T.DEVICE_INSTRUCTIONS_TOGGLE, deviceType }
}

// export function promptDeviceUnlockModal(): ThunkAction {
//   return async (dispatch: any, getState: any) => {
//     const state = getState()
//     const device = state.modal.deviceUnlock.device
//     // throw if it's not there
//     await api.promptPin({ path: device.path })
//   }
// }

export function toggleDeviceUnlockModal() {
  // return { type: T.DEVICE_UNLOCK_TOGGLE }
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
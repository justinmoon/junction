import { ModalActionTypes as T } from './types';
import { Device } from '../../types';
import { ThunkAction } from '../types';
import api from '../../api'

// TODO: this should should hit API and prompt pin if necessary ...
// this could hit all devices with needs_pin_entry ... 
// if showing, require a "device" attribute
// if hiding, remove device attribute

// we need API method to "promptAllDevices"
export function toggleDeviceInstructionsModal() {
  return { type: T.DEVICE_INSTRUCTIONS_TOGGLE }
}

// export function promptDeviceUnlockModal(): ThunkAction {
//   return async (dispatch: any, getState: any) => {
//     const state = getState()
//     const device = state.modal.deviceUnlock.device
//     // throw if it's not there
//     await api.promptPin({ path: device.path })
//   }
// }

export function setDeviceUnlockModalDevice(device: Device) {
  return { type: T.DEVICE_UNLOCK_SET_DEVICE, device: device }
}

export function toggleDeviceUnlockModal() {
  // return { type: T.DEVICE_UNLOCK_TOGGLE }
  return async (dispatch: any, getState: any) => {
    const state = getState()
    const { device, open } = state.modal.deviceUnlock
    if (open) {
      await api.deletePrompt()
    } else {
      // FIXME: throw if it's not there
      await api.promptPin({ path: device.path })
    }
    dispatch({ type: T.DEVICE_UNLOCK_TOGGLE })
  }
}

export function openDeviceUnlockModal(device: Device): ThunkAction {
  return async (dispatch: any) => {
    await dispatch(setDeviceUnlockModalDevice(device))
    // dispatch(promptDeviceUnlockModal())
    await dispatch(toggleDeviceUnlockModal())
  }
}

// would be better to have OPEN and CLOSE types, and a "toggle" action
// that looks up state and calls OPEN and CLOSE depending on state ...

// FIXME: close should fire a DELETE to /prompt and also wipe store
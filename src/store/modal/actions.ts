import { ModalActionTypes as T } from './types';
import { Device } from '../../types';

// TODO: this should should hit API and prompt pin if necessary ...
// this could hit all devices with needs_pin_entry ... 
// if showing, require a "device" attribute
// if hiding, remove device attribute

// we need API method to "promptAllDevices"
export function toggleDeviceInstructionsModal() {
  return { type: T.DEVICE_INSTRUCTIONS_TOGGLE }
}

export function toggleDeviceUnlockModal() {
  return { type: T.DEVICE_UNLOCK_TOGGLE }
}

export function setDeviceUnlockModalDevice(device: Device) {
  return { type: T.DEVICE_UNLOCK_SET_DEVICE, device: device} 
}
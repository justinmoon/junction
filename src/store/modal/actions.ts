import { ModalActionTypes as T, ModalNames } from './types';
import { DeviceType } from '../../types';
import api from '../../api'
import { selectActiveWallet } from '../wallet';
import { notNull } from '..';

export function toggle(modalName: ModalNames, data?: any) {
  return { type: T.TOGGLE, modalName, data }
}

export function toggleDeviceInstructionsModal(deviceType?: DeviceType) {
  const data = { deviceType }
  return toggle(ModalNames.deviceInstructions, data)
}

export function toggleDeviceUnlockModal() {
  return async (dispatch: any, getState: any) => {
    const state = getState()
    const wallet_name = notNull(selectActiveWallet(state)).name
    const { open } = state.modal.deviceUnlock
    if (open) {
      await api.deletePrompt()
    } else {
      await api.promptPin({ wallet_name })
    }
    dispatch(toggle(ModalNames.deviceUnlock))
  }
}

export function toggleDisplayAddressModal(address?: any) {
  const data = { address }
  return toggle(ModalNames.displayAddress, data)
}
export enum ModalActionTypes {
  DEVICE_INSTRUCTIONS_TOGGLE = 'DEVICE_INSTRUCTIONS_TOGGLE',
  DEVICE_UNLOCK_TOGGLE = 'DEVICE_UNLOCK_TOGGLE',
  DEVICE_UNLOCK_SET_DEVICE = 'DEVICE_UNLOCK_SET_DEVICE',
  TOGGLE = 'TOGGLE',
}

// FIXME: should I reference these in the reducer?
export enum ModalNames {
  deviceInstructions = 'deviceInstructions',
  deviceUnlock = 'deviceUnlock',
  displayAddress = 'displayAddress',
  connectRPC = 'connectRPC'
}
import React from 'react';
import { connect } from 'react-redux';
import { Button, Spinner, Row } from 'reactstrap';
import { Device } from '../types'
import { MyCard, MyTable } from './Toolbox'
import DeviceInstructionsModal from './DeviceInstructionsModal'
import EnterPinModal from './EnterPinModal'
import { toggleDeviceInstructionsModal, toggleDeviceUnlockModal, setDeviceUnlockModalDevice } from '../store/modal'
import api from '../api';
import { AppState } from '../store';

interface AddDeviceProps {
  device: Device;
  showSpinner: boolean;
  displayPinEntry(): any;
  addSigner: (device: Device) => void;
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
}

class AddDevice extends React.Component<AddDeviceProps> {
  handleUnlock(device: Device) {
    api.promptPin({ path: device.path }).then(this.props.displayPinEntry)
  }

  render() {
    const { device, showSpinner, displayPinEntry, addSigner } = this.props;
    let rightComponent = null;
    if (showSpinner) {
      rightComponent = <Spinner size="sm"/>;
    } else {
      if (device.needs_pin_sent) {
        rightComponent = <Button onClick={() => this.handleUnlock(device)}>Unlock</Button>
      // TODO
      // } else if (device.needs_pin_sent) {
      //   rightComponent = <Button onClick={enterPassphrase}>Unlock</Button> 
      } else if (device.error) {
        rightComponent = <Button color="default" onClick={this.props.toggleDeviceInstructionsModal}>Unavailable</Button>
      } else {
        rightComponent = <Button onClick={() => addSigner(device)}>Add Signer</Button>
      }
    }
    return (
      <tr key={device.path + device.type}>
        <td>{ device.type }</td>
        <td className="text-right">
          {rightComponent}
        </td>
      </tr>
    )
  }
}

interface Props {
  // Props
  devices: Device[];
  deviceError: Error | null;
  deviceBeingAdded: Device | null;
  addSigner: (device: Device) => void;
}

interface DispatchProps {
  setDeviceUnlockModalDevice: typeof setDeviceUnlockModalDevice; 
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
  toggleDeviceUnlockModal: typeof toggleDeviceUnlockModal;
}

interface StateProps {
  modal: AppState['modal'];
}

type AllProps = Props & StateProps & DispatchProps;

class AddSigners extends React.Component<AllProps> {

  openDeviceUnlockModal(device: Device) {
    this.props.setDeviceUnlockModalDevice(device);
    this.props.toggleDeviceUnlockModal()
  }

  render() {
    // FIXME: use deviceError
    const { devices, deviceBeingAdded, addSigner, deviceError, toggleDeviceInstructionsModal } = this.props;
    
    // FIXME: two instances of <DeviceInstructionsModal/>
    if (!devices || !devices.length) {
      return (
        <MyCard>
          <h5 className='text-center'>No devices available</h5>
          <Row>
            <Button onClick={toggleDeviceInstructionsModal.bind(this)} className='mx-auto'>
              Show instructions
            </Button>
          </Row>
          <DeviceInstructionsModal isOpen={this.props.modal.deviceInstructions.open} 
                                   toggle={toggleDeviceInstructionsModal.bind(this)}/>
        </MyCard>
      )
    }

    return (
      <MyTable>
        <thead>
          <tr>
            <th scope="col">Device</th>
            <th scope="col" className="text-right">Action</th>
          </tr>
        </thead>
        <tbody>
          {devices.map((device: Device) => <AddDevice
                  device={device}
                  showSpinner={device === deviceBeingAdded}
                  displayPinEntry={() => this.openDeviceUnlockModal(device)}
                  addSigner={addSigner.bind(this)}
                  toggleDeviceInstructionsModal={toggleDeviceInstructionsModal.bind(this)}
                  />
          )}
          <EnterPinModal/>
          <DeviceInstructionsModal isOpen={this.props.modal.deviceInstructions.open} 
                                   toggle={toggleDeviceInstructionsModal.bind(this)}/>
        </tbody>
      </MyTable>
    )
  }
}

export const mapStateToProps = (state: AppState) => {
  return {
    modal: state.modal
  }
}

export default connect(
  mapStateToProps,
  { toggleDeviceInstructionsModal, toggleDeviceUnlockModal, setDeviceUnlockModalDevice },
)(AddSigners);
import React from 'react';
import { Button, Spinner, Row } from 'reactstrap';
import { Device } from '../types'
import { MyCard, MyTable } from './Toolbox'
import DeviceInstructionsModal from './DeviceInstructionsModal'
import EnterPinModal from './EnterPinModal'

import api from '../api';

interface AddDeviceProps {
  device: Device;
  showSpinner: boolean;
  displayPinEntry(): any;
  addSigner: (device: Device) => void;
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
        rightComponent = <Button color="danger" onClick={() => alert(device.error)}>Error</Button>
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
  devices: Device[];
  deviceError: Error | null;
  deviceBeingAdded: Device | null;
  addSigner: (device: Device) => void;
}

interface State {
  modal: boolean;
  pinModalActive: boolean;
  // FIXME: keeping track of the device outside the modal sucks
  pinEntryDevice: Device | null;
}

export default class AddSigners extends React.Component<Props, State> {
  state: State = {
    modal: false,
    pinModalActive: false,
    pinEntryDevice: null,
  }

  toggle() {
    this.setState(prevState => ({
      modal: !prevState.modal
    }));
  }

  togglePinModal() {
    this.setState(prevState => ({
      pinModalActive: !prevState.pinModalActive
    }));
  }

  openModal(device: Device) {
    this.togglePinModal();
    this.setState({ pinEntryDevice: device });
  }

  render() {
    // FIXME: use deviceError
    const { devices, deviceBeingAdded, addSigner, deviceError } = this.props;
    
    if (!devices || !devices.length) {
      return (
        <MyCard>
          <h5 className='text-center'>No devices available</h5>
          <Row>
            <Button onClick={this.toggle.bind(this)} className='mx-auto'>
              Show instructions
            </Button>
          </Row>
          <DeviceInstructionsModal isOpen={this.state.modal} toggle={this.toggle.bind(this)}/>
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
                  displayPinEntry={() => this.openModal(device)}
                  addSigner={addSigner.bind(this)}/>
          )}
          <EnterPinModal isOpen={this.state.pinModalActive}
                        toggle={this.togglePinModal.bind(this)}
                        device={this.state.pinEntryDevice}/>
        </tbody>
      </MyTable>
    )
  }
}
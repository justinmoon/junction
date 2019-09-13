import React from 'react';
import { Button, Spinner, Row } from 'reactstrap';
import { Device } from '../types'
import { MyCard, MyTable } from './Toolbox'
import DeviceInstructionsModal from './DeviceInstructionsModal'

interface AddDeviceProps {
  device: Device;
  showSpinner: boolean;
  enterPin(): any;
  addSigner: (device: Device) => void;
}

class AddDevice extends React.Component<AddDeviceProps> {
  render() {
    const { device, showSpinner, enterPin, addSigner } = this.props;
    let rightComponent = null;
    if (showSpinner) {
      rightComponent = <Spinner size="sm"/>;
    } else {
      if (device.needs_pin_sent) {
        rightComponent = <Button onClick={enterPin}>Unlock</Button> 
      // TODO
      // } else if (device.needs_pin_sent) {
      //   rightComponent = <Button onClick={enterPassphrase}>Unlock</Button> 
      } else {
        rightComponent = <Button onClick={() => addSigner(device)}>Add Signer</Button>
      }
    }
    return (
      <tr key={device.fingerprint}>
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
}

export default class AddSigners extends React.Component<Props, State> {
  state: State = {
    modal: false,
  }

  toggle() {
    this.setState(prevState => ({
      modal: !prevState.modal
    }));
  }

  enterPin() {
    console.log('enter pin')
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
          {/* <PinEntryModal isOpen={this.state.pinEntryModal} toggle={this.togglePinEntryModal.bind(this)}/> */}
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
                enterPin={this.enterPin}
                addSigner={addSigner.bind(this)}/>
        )}
        </tbody>
      </MyTable>
    )
  }
}
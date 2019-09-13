import React from 'react';
import { Button, Spinner, Row } from 'reactstrap';
import { Device } from '../types'
import { MyCard, MyTable } from './Toolbox'
import DeviceInstructionsModal from './DeviceInstructionsModal'

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
  render() {
    // FIXME: use deviceError
    const { devices, deviceBeingAdded, deviceError } = this.props;

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
        {devices.map((device: Device) => 
          <tr key={device.fingerprint}>
            <td>{ device.type }</td>
            <td className="text-right">
              {device !== deviceBeingAdded && <Button onClick={() => this.props.addSigner(device)}>Add Signer</Button>}
              {device === deviceBeingAdded && <Spinner size="sm"/>}
            </td>
          </tr>
        )}
        </tbody>
      </MyTable>
    )
  }
}
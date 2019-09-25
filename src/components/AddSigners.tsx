import React from 'react';
import { connect } from 'react-redux';
import { Button, Spinner, Row } from 'reactstrap';
import { Device } from '../types'
import { MyCard, MyTable } from './Toolbox'
import { 
  toggleDeviceInstructionsModal, toggleDeviceUnlockModal
} from '../store/modal'
import { AppState } from '../store';

interface Props {
  devices: Device[];
  deviceError: Error | null;
  deviceBeingAdded: Device | null;
  addSigner: (device: Device) => void;
}

interface DispatchProps {
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
  toggleDeviceUnlockModal: any;  // FIXME
}

interface StateProps {
  modal: AppState['modal'];
}

type AllProps = Props & StateProps & DispatchProps;

class AddSigners extends React.Component<AllProps> {

  renderAddDevice(device: Device) {
    const { addSigner, deviceBeingAdded, toggleDeviceInstructionsModal, toggleDeviceUnlockModal } = this.props;
    const showSpinner = device === deviceBeingAdded;
    let rightComponent = null;
    if (showSpinner) {
      rightComponent = <Spinner size="sm"/>;
    } else {
      // TODO: passwords
      if (device.needs_pin_sent) {
        rightComponent = <Button onClick={() => toggleDeviceUnlockModal()}>Unlock</Button>
      } else if (device.error) {
        rightComponent = <Button color="default" onClick={() => toggleDeviceInstructionsModal(device.type)}>
          Unavailable
        </Button>
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

  render() {
    // FIXME: use deviceError
    const { devices, toggleDeviceInstructionsModal } = this.props;
    
    // FIXME: two instances of <DeviceInstructionsModal/>
    if (!devices || !devices.length) {
      return (
        <MyCard>
          <h5 className='text-center'>No devices available</h5>
          <Row>
            <Button onClick={() => toggleDeviceInstructionsModal()} className='mx-auto'>
              Show instructions
            </Button>
          </Row>
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
          {devices.map((device: Device) => this.renderAddDevice(device))}
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
  { toggleDeviceInstructionsModal, 
    toggleDeviceUnlockModal },
)(AddSigners);
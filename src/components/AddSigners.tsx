import React from 'react';
import { connect } from 'react-redux';
import { Button, Row } from 'reactstrap';
import { Device, isUnlockedDevice } from '../types'
import { MyCard, MyTable, LoadingButton } from './Toolbox'
import { 
  toggleDeviceInstructionsModal, toggleDeviceUnlockModal
} from '../store/modal'
import { AppState } from '../store';
import { selectCandidateDevicesForActiveWallet, addSigner } from '../store/wallet';

interface DispatchProps {
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
  toggleDeviceUnlockModal: any;  // FIXME
  addSigner: typeof addSigner;
}

interface StateProps {
  modal: AppState['modal'];
  devices: AppState['device']['devices']['data'];
  deviceBeingAdded: Device | null;
}

type Props = StateProps & DispatchProps;

class AddSigners extends React.Component<Props> {

  renderAddDevice(device: Device) {
    const { addSigner, deviceBeingAdded, toggleDeviceInstructionsModal, toggleDeviceUnlockModal } = this.props;
    const loading = device === deviceBeingAdded;
    let rightComponent = null;
    
    // TODO: passwords
    if (device.needs_pin_sent) {
      rightComponent = <Button onClick={() => toggleDeviceUnlockModal()}>Unlock</Button>
    } else if (device.error) {
      rightComponent = <Button color="default" onClick={() => toggleDeviceInstructionsModal(device.type)}>Unavailable</Button>
    } else if (isUnlockedDevice(device)) {
      rightComponent = <LoadingButton loading={loading} onClick={() => addSigner(device)}>Add Signer</LoadingButton>
    } else {
      return <div></div> // FIXME
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
    if (!devices) {
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
    modal: state.modal,
    devices: selectCandidateDevicesForActiveWallet(state),
    deviceBeingAdded: state.wallet.addSigner.device,
  }
}

export default connect(
  mapStateToProps,
  { toggleDeviceInstructionsModal, 
    toggleDeviceUnlockModal,
    addSigner },
)(AddSigners);
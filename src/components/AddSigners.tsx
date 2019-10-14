import React from 'react';
import { connect } from 'react-redux';
import { Button, Row, Input } from 'reactstrap';
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

interface LocalState {
  nicknames: {
    [key: string]: string;
  }
}

class AddSigners extends React.Component<Props,LocalState> {
  state: LocalState = {
    nicknames: {}
  }

  private setNickname = (ev: React.ChangeEvent<HTMLInputElement>, device: Device) => {
    this.setState({ 
      nicknames: {
        ...this.state.nicknames,
        [device.path]: ev.target.value
      }
    });
  };

  private addSigner = (device: Device, nickname: string) => {
    if (nickname.length === 0) {
      alert('Give your device a nickname')
    } else if (isUnlockedDevice(device)) {  // FIXME: typescript sucks
      this.props.addSigner(device, nickname)
    }
  };

  renderAddDevice(device: Device) {
    const { deviceBeingAdded, toggleDeviceInstructionsModal, toggleDeviceUnlockModal } = this.props;
    const loading = device === deviceBeingAdded;
    let rightComponent = null;
    let nickname = this.state.nicknames[device.path] || ''

    // TODO: passwords
    if (device.needs_pin_sent) {
      rightComponent = <Button onClick={() => toggleDeviceUnlockModal()}>Unlock</Button>
    } else if (device.error) {
      rightComponent = <Button color="default" onClick={() => toggleDeviceInstructionsModal(device.type)}>Unavailable</Button>
    } else if (isUnlockedDevice(device)) {
      rightComponent = <LoadingButton loading={loading} onClick={() => this.addSigner(device, nickname)}>Add Signer</LoadingButton>
    } else {
      return <div></div> // FIXME
    }

    return (
      <tr key={device.path + device.type}>
        <td>{ device.type }</td>
        <td>
          {device.path && <Input name="host" type="text" value={nickname} onChange={e => this.setNickname(e, device)}/>}   
        </td>
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
            <th scope="col">Nickname</th>
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
    error: state.wallet.addSigner.error,
  }
}

export default connect(
  mapStateToProps,
  { toggleDeviceInstructionsModal, 
    toggleDeviceUnlockModal,
    addSigner },
)(AddSigners);
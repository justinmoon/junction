import React from 'react';
import { connect } from 'react-redux';
import { Button, Row } from 'reactstrap';
import { Device, isUnlockedDevice, Signer, DeviceType } from '../types'
import { MyCard, MyTable, LoadingButton } from './Toolbox'
import { 
  toggleDeviceInstructionsModal, toggleDeviceUnlockModal
} from '../store/modal'
import { AppState, notNull } from '../store';
import { registerSigner, selectUnregisteredSigners, deviceAvailable } from '../store/wallet';
import { selectDevices } from '../store/device';

interface DispatchProps {
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
  registerSigner: typeof registerSigner;
}

interface StateProps {
  modal: AppState['modal'];
  devices: Device[];
  signers: Signer[];
  signerBeingRegistered: Signer | null;
}

type Props = StateProps & DispatchProps;

class RegisterSigners extends React.Component<Props> {

  async registerSigner(signer: Signer) {
    alert("Confirm multisig wallet on your Device")
    await this.props.registerSigner(signer)
  }
  renderAddSigner(signer: Signer) {
    const { registerSigner, signerBeingRegistered, toggleDeviceInstructionsModal, devices } = this.props;
    const loading = signer === signerBeingRegistered;
    let rightComponent = null;
    const device = deviceAvailable(signer, devices)
    
    if (device === null) {
      rightComponent = <Button color="default" onClick={() => toggleDeviceInstructionsModal(DeviceType.coldcard)}>Unavailable</Button>
    } else if (isUnlockedDevice(device)) {
      rightComponent = <LoadingButton loading={loading} onClick={() => this.registerSigner(signer)}>Register</LoadingButton>
    } else {
      return <div></div> // FIXME
    }
    
    return (
      <tr key={signer.fingerprint}>
        <td>{ signer.name }</td>
        <td className="text-right">
          {rightComponent}
        </td>
      </tr>
    )
  }

  render() {
    // FIXME: use deviceError
    const { signers } = this.props;

    return (
      <MyTable>
        <thead>
          <tr>
            <th scope="col">Device</th>
            <th scope="col" className="text-right">Action</th>
          </tr>
        </thead>
        <tbody>
          {signers.map((signer: Signer) => this.renderAddSigner(signer))}
        </tbody>
      </MyTable>
    )
  }
}

export const mapStateToProps = (state: AppState) => {
  return {
    modal: state.modal,
    signers: selectUnregisteredSigners(state),
    signerBeingRegistered: state.wallet.registerSigner.signer,
    devices: notNull(selectDevices(state)),
  }
}

export default connect(
  mapStateToProps,
  { toggleDeviceInstructionsModal, 
    registerSigner },
)(RegisterSigners);

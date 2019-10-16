import React from 'react';
import { Button, Modal, ModalHeader, ModalFooter, ModalBody, Table } from 'reactstrap';
import { AppState, notNull } from '../store';
import { toggleDisplayAddressModal, toggleDeviceInstructionsModal, toggleDeviceUnlockModal } from '../store/modal'
import { connect } from 'react-redux';
import { Device, isUnlockedDevice, UnlockedDevice, Signer, Wallet } from '../types';
import api from '../api'
import { selectDevices } from '../store/device';
import { LoadingButton } from './Toolbox';
import { selectActiveWallet, deviceAvailable } from '../store/wallet';

interface DispatchProps {
  toggleDisplayAddressModal: typeof toggleDisplayAddressModal;
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
  toggleDeviceUnlockModal: any;  // FIXME
}

interface StateProps {
  open: AppState['modal']['displayAddress']['open'];
  address: string | null;
  devices: Device[] | null;
  activeWallet: Wallet | null;
}

type Props = DispatchProps & StateProps

interface LocalState {
  displayAddressDevice: Device | null;
  message: string | null;
}

class DisplayAddressModal extends React.Component<Props> {
  state: LocalState = {
    displayAddressDevice: null,
    message: null,
  };

  async displayAddress(address: string, device: UnlockedDevice, signer: Signer, activeWallet: Wallet) {
    // FIXME: all these parameters b/c typescript won't let me read from props ...
    this.setState({ 
      displayAddressDevice: device,
      message: `Verify address on your "${signer.name}" ${device.type} device`
    })
    // FIXME: handle errors
    await api.displayAddress({address, device_id: device.fingerprint, wallet_name: activeWallet.name})
    this.setState({
      displayAddressDevice: null,
    })
  }

  renderSigner(address: string, devices: Device[], signer: Signer, activeWallet: Wallet) {
    // FIXME: all these parameters b/c typescript won't let me read from props ...
    const {
      toggleDeviceInstructionsModal, toggleDeviceUnlockModal
    } = this.props;

    let rightComponent = null;
    const device = deviceAvailable(signer, devices)
    const loading = this.state.displayAddressDevice && this.state.displayAddressDevice == device;
    if (activeWallet.wallet_type === 'multi' && (signer.type !== 'trezor' && signer.type !== 'coldcard')) {
      rightComponent =<div>Not supported by {signer.type} devices</div>
    } else if (device) {
      rightComponent = <LoadingButton loading={loading} onClick={() => this.displayAddress(address, device, signer, activeWallet)}>Display</LoadingButton>
    } else if (signer.type == 'trezor') {
      rightComponent =<Button onClick={() => toggleDeviceUnlockModal()}>Unlock</Button>
    } else if (device === null) {
      rightComponent = <Button color="default" onClick={() => toggleDeviceInstructionsModal()}>Unavailable</Button>
    } else {
      return <div></div> // FIXME
    }
    
    return (
      <tr key={signer.name}>
        <td>{ signer.name }</td>
        <td className="text-right">
          {rightComponent}
        </td>
      </tr>
    )
  }

  render() {
    const { toggleDisplayAddressModal, open, address, activeWallet, devices } = this.props;

    if (!address || devices === null || activeWallet === null) {
      return <div></div>
    }

    return (
			<Modal isOpen={open} toggle={() => toggleDisplayAddressModal()} size="lg"  style={{maxWidth: '1000px', width: '80%'}}>
				<ModalHeader toggle={() => toggleDisplayAddressModal()}>Display Address</ModalHeader>
				<ModalBody>
          <div>{address}</div>
          <h6>Display on Device</h6>
          <Table borderless>
            <tbody>
              {activeWallet.signers.map((signer: Signer) => this.renderSigner(address, devices, signer, activeWallet))}
            </tbody>
          </Table>
				</ModalBody>
				<ModalFooter>
					<Button color="secondary" onClick={() => toggleDisplayAddressModal()}>OK</Button>
				</ModalFooter>
			</Modal>
		)
	}
}

export const mapStateToProps = (state: AppState) => {
	return {
    open: state.modal.displayAddress.open,
    address: state.modal.displayAddress.address,
    devices: state.device.devices.data,
    activeWallet: selectActiveWallet(state),
	}
}
  
export default connect(
	mapStateToProps,
	{ toggleDisplayAddressModal, toggleDeviceInstructionsModal, toggleDeviceUnlockModal },
)(DisplayAddressModal);
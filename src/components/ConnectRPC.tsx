import React from 'react';
import { Button, Modal, ModalHeader, ModalFooter, ModalBody } from 'reactstrap';
import { AppState } from '../store';
import { toggleDeviceInstructionsModal } from '../store/modal'
import { connect } from 'react-redux';
import { selectActiveWallet } from '../store/wallet';
import {  Wallet } from '../types';

interface DispatchProps {
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
}

interface StateProps {
  activeWallet: Wallet | null;
}

type Props = DispatchProps & StateProps

class DeviceInstructionsModal extends React.Component<Props> {
  render() {
    const { activeWallet, toggleDeviceInstructionsModal } = this.props;
    if (!activeWallet) {
      return <div></div>
    }
    const rpcError = activeWallet.node.rpc_error
    const hasRpcError = !!rpcError
    console.log("RPC ERROR", hasRpcError)
    return (
			<Modal isOpen={hasRpcError} toggle={() => {}}>
				<ModalHeader toggle={() => {}}>Node Connection Problem</ModalHeader>
				<ModalBody>
          {rpcError}
				</ModalBody>
				<ModalFooter>
					<Button color="secondary" onClick={() => {}}>OK</Button>
				</ModalFooter>
			</Modal>
		)
	}
}

export const mapStateToProps = (state: AppState) => {
	return {
    activeWallet: selectActiveWallet(state),
	}
}
  
export default connect(
	mapStateToProps,
	{ toggleDeviceInstructionsModal },
)(DeviceInstructionsModal);
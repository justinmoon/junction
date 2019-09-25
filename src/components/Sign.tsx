import React from 'react';
import { connect } from 'react-redux';
import { withRouter, RouteComponentProps } from 'react-router';
import { Button,  Tooltip,  Spinner } from 'reactstrap';
import { getWallets, selectActiveWallet, signPSBT, broadcastTransaction } from '../store/wallet';
import { toggleDeviceInstructionsModal, toggleDeviceUnlockModal } from '../store/modal';
import { AppState } from '../store';
import { MyTable } from './Toolbox'
import { Wallet, Signer, Device } from '../types';
import './Sign.css'

interface DispatchProps {
  getWallets: typeof getWallets;
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
  signPSBT: typeof signPSBT;
  toggleDeviceUnlockModal: any;  // FIXME
  broadcastTransaction: any;
}

type Props = DispatchProps & StateProps & RouteComponentProps;

interface StateProps {
  activeWallet: Wallet | null;
  devices: AppState['device']['devices']['data'];
  signPSBTState: AppState['wallet']['signPSBT'];
  broadcastTransactionState: AppState['wallet']['broadcastTransaction'];
}

interface LocalState {
  isSubmitting: boolean;
  error: Error | null;
  tooltipOpen: boolean;
}

function signedBySigner(signer: Signer, psbt: any) {
  for (let input of psbt.inputs) {
    let signed = false;
    for (let deriv of input.bip32_derivs) {
      const fingerprintMatch = deriv.master_fingerprint == signer.fingerprint;
      if (!input.partial_signatures) {
        return false;
      }
      const pubkeyMatch = deriv.pubkey in input.partial_signatures
      if (fingerprintMatch && pubkeyMatch) {
        signed = true
      }
    }
    // return false if any input is unsigned
    if (!signed) return false;
  }
  // if every input is signed, return true
  return true;
}

function deviceAvailable(signer: Signer, devices: Device[]) {
  // look for a device with fingerprint matching signer's fingerprint
  for (let device of devices) {
    // FIXME: this check sucks
    if ('fingerprint' in device && device.fingerprint === signer.fingerprint) {
      return device
    }
  }
  return null;
}

class Sign extends React.Component<Props, LocalState> {
  state: LocalState = {
    isSubmitting: false,
    error: null,
    tooltipOpen: false,
  };

  toggleTooltip() {
    this.setState({
      tooltipOpen: !this.state.tooltipOpen,
    })
  }

  renderSigner(signer: Signer, psbt: any, devices: Device[]) {
    const device = deviceAvailable(signer, devices)
    const { activeWallet, toggleDeviceInstructionsModal, signPSBT, toggleDeviceUnlockModal, signPSBTState } = this.props
    const signed = signedBySigner(signer, psbt)
    if (signed) {
      return (
        <tr key={signer.fingerprint}>
          <td>{ signer.name }</td>
          <td className="text-right">Signed</td>
        </tr>
      )
    } else if (activeWallet && activeWallet.signatures_remaining === 0 && !signed) {
      return (
        <tr key={signer.fingerprint}>
          <td>{ signer.name }</td>
          <td className="text-right">Didn't sign</td>
        </tr>
      )
    } else if (device && signPSBTState.device && device.fingerprint == signPSBTState.device.fingerprint) {
      return (
        <tr key={signer.name}>
          <td>{ signer.name }</td>
          <td className="text-right">
            <Spinner />
          </td>
        </tr>
      )
    } else if (device && device.fingerprint) {
      return (
        <tr key={signer.name}>
          <td>{ signer.name }</td>
          <td className="text-right">
            <Button onClick={() => signPSBT(device)}>Sign</Button>
          </td>
        </tr>
      )
    } else if (signer.type == 'trezor') {
      return (
        <tr key={signer.name}>
          <td>{ signer.name }</td>
          <td className="text-right">
            <Button onClick={() => toggleDeviceUnlockModal()}>Unlock</Button>
          </td>
        </tr>
      )
    } else {
      return (
        <tr key={signer.name}>
          <td>{ signer.name }</td>
          <td className="text-right">
            <Button onClick={() => toggleDeviceInstructionsModal(signer.type)}>Unlock</Button>
          </td>
        </tr>
      )
    }
  }

  broadcastTransaction() {
    const { activeWallet, broadcastTransaction } = this.props
    if (activeWallet && !activeWallet.signatures_remaining) {
      broadcastTransaction()
    }
  }

  render() {
    const { activeWallet, devices, broadcastTransactionState } = this.props;
    if (!activeWallet || !devices) {
      return <div>loading</div>
    }
    if (!activeWallet.psbt) {
      return <div>no psbt</div>
    }
    const { psbt, signers } = activeWallet;
    
    return (
      <div>
        <MyTable>
          <tbody>
            <h4>Outputs</h4>
            {psbt.tx.vout.map((vout: any, index: number) => (
              <tr key={index}>
                <td>#{ index }</td>
                <td>{ vout.scriptPubKey.addresses[0] }</td>
                <td className="text-right">{ vout.value } BTC</td>
              </tr>
            ))}
            <h4>Signatures</h4>
            {signers.map((signer: Signer) => this.renderSigner(signer, psbt, devices))}
          </tbody>
        </MyTable>
        <div className="d-flex">
              
          {!broadcastTransactionState.pending && <Button onClick={() => this.broadcastTransaction()} color="primary" id="broadcast"
                  className="ml-auto">
            Broadcast
          </Button>}
          {broadcastTransactionState.pending && 
            <Spinner className="ml-auto"/>}
          {!!activeWallet.signatures_remaining && 
            <Tooltip placement="left" isOpen={this.state.tooltipOpen} target="broadcast" 
                toggle={() => this.toggleTooltip()}>
              Add {activeWallet.signatures_remaining} signatures before broadcasting
            </Tooltip>}
        </div>
      </div>
    )
  }
}

const ConnectedSign = connect<StateProps, DispatchProps, RouteComponentProps, AppState>(
  state => ({
    activeWallet: selectActiveWallet(state),
    devices: state.device.devices.data,
    signPSBTState: state.wallet.signPSBT,
    broadcastTransactionState: state.wallet.broadcastTransaction,
  }),
  { getWallets, toggleDeviceInstructionsModal, signPSBT, toggleDeviceUnlockModal, broadcastTransaction },
)(Sign);

export default withRouter(ConnectedSign)
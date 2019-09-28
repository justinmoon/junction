import React from 'react';
import { connect } from 'react-redux';
import { withRouter, RouteComponentProps } from 'react-router';
import { Button,  Tooltip, Table } from 'reactstrap';
import { getWallets, selectActiveWallet, signPSBT, broadcastTransaction } from '../store/wallet';
import { toggleDeviceInstructionsModal, toggleDeviceUnlockModal } from '../store/modal';
import { AppState, notNull } from '../store';
import { MyCard, LoadingButton } from './Toolbox'
import { Wallet, Signer, Device } from '../types';
import './Sign.css'
import { selectDevices } from '../store/device';


interface DispatchProps {
  getWallets: typeof getWallets;
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
  signPSBT: typeof signPSBT;
  toggleDeviceUnlockModal: any;  // FIXME
  broadcastTransaction: any;
}

type Props = DispatchProps & StateProps & RouteComponentProps;

interface StateProps {
  activeWallet: Wallet;
  devices: Device[];
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
      const fingerprintMatch = deriv.master_fingerprint === signer.fingerprint;
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
    const didNotSign = activeWallet.signatures_remaining === 0 && !signed
    const isSigning = device !== null && signPSBTState.device && device.fingerprint === signPSBTState.device.fingerprint;
    const canSign = device !== null && device.fingerprint;

    let rightComponent = null

    if (signed) {
      rightComponent = <td className="text-right">Signed</td>
    } else if (didNotSign) {
      rightComponent = <td className="text-right">Didn't sign</td>
    } else if (isSigning) {
      rightComponent = <LoadingButton loading={true}>Sign</LoadingButton>
    } else if (canSign) {
      // FIXME
      if (device !== null) {
        rightComponent = <LoadingButton onClick={canSign ? () => signPSBT(device) : () => {}}>Sign</LoadingButton>
      } else {
        rightComponent = <div/>
      }
    } else if (signer.type === 'trezor') {
      rightComponent =<Button onClick={() => toggleDeviceUnlockModal()}>Unlock</Button>
    } else {
      rightComponent = <Button onClick={() => toggleDeviceInstructionsModal(signer.type)}>Unlock</Button>
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

  broadcastTransaction() {
    const { activeWallet, broadcastTransaction } = this.props
    if (activeWallet.signatures_remaining === 0) {
      broadcastTransaction()
    }
  }

  render() {
    const { activeWallet, devices, broadcastTransactionState } = this.props;
    if (!activeWallet.psbt) {
      return <div>no psbt</div>
    }
    const { psbt, signers } = activeWallet;
    
    return (
      <MyCard>
        <h4>Outputs</h4>
        <Table borderless>
          <tbody>
            {psbt.tx.vout.map((vout: any, index: number) => (
              <tr key={index}>
                <td>#{ index }</td>
                <td>{ vout.scriptPubKey.addresses[0] }</td>
                <td className="text-right">{ vout.value } BTC</td>
              </tr>
            ))}
            </tbody>
        </Table>

        <h4>Signatures ({activeWallet.m - activeWallet.signatures_remaining}/{activeWallet.m})</h4>
        <Table borderless>
          <tbody>
            {signers.map((signer: Signer) => this.renderSigner(signer, psbt, devices))}
          </tbody>
        </Table>

        <div className="d-flex">
          <LoadingButton loading={broadcastTransactionState.pending} onClick={() => this.broadcastTransaction()} color="primary" id="broadcast"
                  className="ml-auto">
            Broadcast
          </LoadingButton>
          {!!activeWallet.signatures_remaining && 
            <Tooltip placement="left" isOpen={this.state.tooltipOpen} target="broadcast" 
                toggle={() => this.toggleTooltip()}>
              Add {activeWallet.signatures_remaining} signatures before broadcasting
            </Tooltip>}
        </div>
      </MyCard>
    )
  }
}

const ConnectedSign = connect<StateProps, DispatchProps, RouteComponentProps, AppState>(
  state => ({
    activeWallet: notNull(selectActiveWallet(state)),
    devices: notNull(selectDevices(state)),
    signPSBTState: state.wallet.signPSBT,
    broadcastTransactionState: state.wallet.broadcastTransaction,
  }),
  { getWallets, toggleDeviceInstructionsModal, signPSBT, toggleDeviceUnlockModal, broadcastTransaction },
)(Sign);

export default withRouter(ConnectedSign)
import React from 'react';
import { connect } from 'react-redux';
import { withRouter, RouteComponentProps } from 'react-router';
import { Form, FormGroup, Input, Label, Button, Row, Col } from 'reactstrap';
import { getWallets } from '../store/wallet';
import { AppState } from '../store';
import api, { CreatePSBTOutput } from '../api';
import { MyCard, MyTable } from './Toolbox'
import { Wallet, Signer, Device } from '../types';
import './Send.css'

interface DispatchProps {
  getWallets: typeof getWallets;
}

type Props = DispatchProps & StateProps & RouteComponentProps;

interface StateProps {
  activeWallet: AppState['wallet']['activeWallet'];
  devices: AppState['device']['devices']['data'];
}

interface LocalState {
  isSubmitting: boolean;
  error: Error | null;
}

function signedBySigner(signer: Signer, psbt: any) {
  for (let input of psbt.inputs) {
    let signed = false;
    for (let deriv of input.bip32_derivs) {
      const fingerprintMatch = deriv.master_fingerprint == signer.fingerprint;
      if (!input.partial_signatures) {
        return false;
      }
      const pubkeyMatch = input.partial_signatures.contains(deriv.pubkey);
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
      return true
    }
  }
  return false;
}

class Sign extends React.Component<Props, LocalState> {
  state: LocalState = {
    isSubmitting: false,
    error: null,
  };

  renderSigner(signer: Signer, psbt: any, devices: Device[]) {
    if (signedBySigner(signer, psbt)) {
      return (
        <tr key={signer.fingerprint}>
          <td>{ signer.name }</td>
          <td className="text-right">Signed</td>
        </tr>
      )
    } else if (deviceAvailable(signer, devices)) {
      return (
        <tr>
          <td>{ signer.name }</td>
          <td className="text-right">
            <Button>Sign</Button>
          </td>
        </tr>
      )
    } else {
      return (
        <tr>
          <td>{ signer.name }</td>
          <td className="text-right">
            <Button>Unlock</Button>
          </td>
        </tr>
      )
      }
  }

  render() {
    const { activeWallet, devices } = this.props;
    if (!activeWallet || !devices) {
      return <div>loading</div>
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
      </div>
    )
  }
}

const ConnectedSign = connect<StateProps, DispatchProps, RouteComponentProps, AppState>(
  state => ({
    activeWallet: state.wallet.activeWallet,
    devices: state.device.devices.data,
  }),
  { getWallets },
)(Sign);

export default withRouter(ConnectedSign)
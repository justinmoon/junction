import React from 'react';
import { connect } from 'react-redux';
import { AppState } from '../store';
import { withRouter, RouteComponentProps } from 'react-router';
import api from '../api'
import { walletReducer } from '../store/wallet';
import { Signer, Wallet, Device } from '../types'


interface StateProps {
  candidates: Device[];
  activeWallet: AppState['wallet']['activeWallet'];
}

function selectCandidateDevicesForActiveWallet(state: AppState) {
  // FIXME this check sucks
  if (state.device.devices.data === null || state.wallet.activeWallet === null) {
    return [];
  }
  const walletFingerprints = state.wallet.activeWallet.signers.map((signer: Signer) => signer.fingerprint);
  return state.device.devices.data.reduce(
    (candidates: Device[], device: Device) => {
      if (!walletFingerprints.includes(device.fingerprint)) {
        candidates.push(device);
      }
      return candidates;
  }, [])
}

class AddSigners extends React.Component<StateProps> {
  render() {
    const { activeWallet, candidates } = this.props;
    if (activeWallet === null) {
      return <h5>FIXME: no active wallet</h5>;
    }
    if (candidates === null) {
      return <h5>FIXME: no candidates</h5>;
    }
    return (
      <div>
        {candidates.map((device: Device) => 
          <div key={device.fingerprint}>{device.type}</div>
        )}
      </div>
    )
  }
}

export const mapStateToProps = (state: AppState) => {
  return {
    candidates: selectCandidateDevicesForActiveWallet(state),
    activeWallet: state.wallet.activeWallet,
  }
}

export default connect(
  mapStateToProps,
  {},
)(AddSigners);
import React from 'react';
import { connect } from 'react-redux';
import AddSigners from './AddSigners';
import Signers from './Signers';
import { Device, isUnlockedDevice } from '../types'
import { AppState } from '../store';
import { getWallets, selectCandidateDevicesForActiveWallet, selectActiveWallet } from '../store/wallet';
import api from '../api'

interface StateProps {
  candidateDevices: ReturnType<typeof selectCandidateDevicesForActiveWallet>;
  deviceError: AppState['device']['devices']['error'];
  activeWallet: ReturnType<typeof selectActiveWallet>;
}

interface DispatchProps {
  getWallets: typeof getWallets;
}

interface State {
  deviceBeingAdded: Device | null;
}

type Props = StateProps & DispatchProps;

class Wallet extends React.Component<Props, State> {
  state: State = {
    deviceBeingAdded: null,
  }
  private addSigner = async (device: Device) => {
    if (!this.props.activeWallet || !isUnlockedDevice(device))  {
      return;
    }
    this.setState({ deviceBeingAdded: device })
    await api.addSigner({
      wallet_name: this.props.activeWallet.name,
      signer_name: device.type,
      device_id: device.fingerprint,
    })
    // FIXME: state.wallet.activeWallet goes stale here
    await this.props.getWallets();
  }
  render() {
    const { deviceBeingAdded } = this.state;
    const { candidateDevices, activeWallet, deviceError } = this.props;
    if (!activeWallet) {
      return <div>no active wallet</div>
    }
    const { signers } = activeWallet;

    let signersComponent = null;
    if (signers.length) {
      signersComponent = (
        <div>
          <h3 className='text-center'>Signers</h3>
          <Signers signers={signers} />
        </div>
      )
    }

    // "Add Signers" section
    let addSigners = null;
    if (!activeWallet.ready) {
      addSigners = (
        <div>
          <h3 className='text-center'>Add {activeWallet.n - activeWallet.signers.length} More Signers</h3>
          <AddSigners devices={candidateDevices} deviceError={deviceError}  deviceBeingAdded={deviceBeingAdded} addSigner={this.addSigner}/>
        </div>
      )
    }
    return (
      <div>
        <h2 className='text-center'>{ activeWallet.name } ({activeWallet.m}/{activeWallet.n})</h2>
        {activeWallet.ready && 
          <div>Confirmed Balance: {activeWallet.balances.confirmed}</div>
        }
        {activeWallet.balances.unconfirmed > 0 &&
          <div>Unconfirmed Balance: {activeWallet.balances.unconfirmed}</div>}
        {signersComponent}
        {addSigners}
        </div>
    )
  }
}
  
export const mapStateToProps = (state: AppState) => {
  return {
    candidateDevices: selectCandidateDevicesForActiveWallet(state),
    activeWallet: selectActiveWallet(state),
    deviceError: state.device.devices.error,
  }
}

export default connect(
  mapStateToProps,
  { getWallets },
)(Wallet);
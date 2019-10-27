import React from 'react';
import { connect } from 'react-redux';
import AddSigners from './AddSigners';
import Signers from './Signers';
import { Wallet as WalletType, Signer } from '../types'
import { AppState, notNull } from '../store';
import { LoadingButton } from './Toolbox'
import { getWallets, selectActiveWallet, addSigner, selectUnregisteredSigners, selectNodeProblem } from '../store/wallet';
import api from '../api'
import { toggleDisplayAddressModal, toggleConnectRPCModal } from '../store/modal';
import RegisterSigners from './RegisterSigners';

interface StateProps {
  activeWallet: WalletType;
  unregisteredSigners: Signer[];
  nodeProblem: boolean;
}

interface DispatchProps {
  getWallets: typeof getWallets;
  addSigner: typeof addSigner;
  toggleDisplayAddressModal: typeof toggleDisplayAddressModal;
  toggleConnectRPCModal: typeof toggleConnectRPCModal;
}

interface State {
  pending: boolean;
}

type Props = StateProps & DispatchProps;

class Wallet extends React.Component<Props, State> {
  state: State = {
    pending: false,
  }

  async generateAddress() {
    this.setState({ pending: true })
    try {
      const response = await api.generateAddress({ wallet_name: this.props.activeWallet.name })
      this.props.toggleDisplayAddressModal(response.address)
    } catch(error) {
      console.log(error)
    }
    this.setState({ pending: false })
  }

  render() {
    const { activeWallet, unregisteredSigners, nodeProblem, toggleConnectRPCModal } = this.props;
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
          <AddSigners/>
        </div>
      )
    }

    let registerSigners = null;
    if (activeWallet.ready && unregisteredSigners.length > 0) {
      registerSigners = (
        <div className='text-center'>
          <h3>Register Wallet On-Device</h3>
          <i>Do this once. Junction can't yet detect whether you've done it, so this prompt will remain visible ...</i>
          <RegisterSigners/>
        </div>
      )
    }

    let walletBody = null
    if (nodeProblem) {
      walletBody = (
        <div className="text-center">
          <LoadingButton color="danger" loading={this.state.pending} onClick={() => toggleConnectRPCModal()}>
            Fix Issues With Your Node
          </LoadingButton>
        </div>
      )
    } else {
      walletBody = (<div>
        {activeWallet.ready && 
          <div className="text-center">Confirmed Balance: {activeWallet.balances.confirmed} BTC</div>
        }
        {activeWallet.balances.unconfirmed > 0 &&
          <div className="text-center">Unconfirmed Balance: {activeWallet.balances.unconfirmed} BTC</div>}
        <div className="text-center">Network: {activeWallet.network}</div>
        {activeWallet.ready &&
          <div className="text-center">
            <LoadingButton loading={this.state.pending} onClick={() => this.generateAddress()}>Generate Address</LoadingButton>
          </div>}
      </div>)
    }

    return (
      <div>
        <h2 className='text-center'>{ activeWallet.name } ({activeWallet.m}/{activeWallet.n})</h2>
        {walletBody}
        {signersComponent}
        {addSigners}
        {activeWallet.n > 1 && registerSigners}
        </div>
    )
  }
}
  
const mapStateToProps = (state: AppState) => {
  return {
    activeWallet: notNull(selectActiveWallet(state)),
    unregisteredSigners: selectUnregisteredSigners(state),
    nodeProblem: selectNodeProblem(state),
  }
}

export default connect(
  mapStateToProps,
  { getWallets, toggleDisplayAddressModal, toggleConnectRPCModal },
)(Wallet);
import React from 'react';
import { connect } from 'react-redux';
import AddSigners from './AddSigners';
import Signers from './Signers';
import { Wallet as WalletType, Signer, WalletType as WalletTypeType } from '../types'
import { AppState, notNull } from '../store';
import { LoadingButton } from './Toolbox'
import { getWallets, selectActiveWallet, addSigner, selectUnregisteredSigners } from '../store/wallet';
import api from '../api'
import { toggleDisplayAddressModal } from '../store/modal';
import RegisterSigners from './RegisterSigners';

interface StateProps {
  activeWallet: WalletType;
  unregisteredSigners: Signer[];
}

interface DispatchProps {
  getWallets: typeof getWallets;
  addSigner: typeof addSigner;
  toggleDisplayAddressModal: typeof toggleDisplayAddressModal;
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
    const { activeWallet, unregisteredSigners } = this.props;
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
        <div>
          <h3 className='text-center'>Register Wallet On-Device</h3>
          <RegisterSigners/>
        </div>
      )
    }

    return (
      <div>
        <h2 className='text-center'>{ activeWallet.name } ({activeWallet.m}/{activeWallet.n})</h2>
        {activeWallet.ready && 
          <div className="text-center">Confirmed Balance: {activeWallet.balances.confirmed} BTC</div>
        }
        {activeWallet.balances.unconfirmed > 0 &&
          <div className="text-center">Unconfirmed Balance: {activeWallet.balances.unconfirmed} BTC</div>}
        {activeWallet.ready &&
          <div className="text-center">
            <LoadingButton loading={this.state.pending} onClick={() => this.generateAddress()}>Generate Address</LoadingButton>
          </div>}
        {activeWallet.node.rpc_error && <div>rpc error: {activeWallet.node.rpc_error}</div>}
        {signersComponent}
        {addSigners}
        {activeWallet.wallet_type === WalletTypeType.multi && registerSigners}
        </div>
    )
  }
}
  
const mapStateToProps = (state: AppState) => {
  return {
    activeWallet: notNull(selectActiveWallet(state)),
    unregisteredSigners: selectUnregisteredSigners(state),
  }
}

export default connect(
  mapStateToProps,
  { getWallets, toggleDisplayAddressModal },
)(Wallet);
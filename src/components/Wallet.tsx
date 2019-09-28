import React from 'react';
import { connect } from 'react-redux';
import AddSigners from './AddSigners';
import Signers from './Signers';
import { Wallet as WalletType } from '../types'
import { AppState, notNull } from '../store';
import { LoadingButton } from './Toolbox'
import { getWallets, selectActiveWallet, addSigner } from '../store/wallet';
import api from '../api'

interface StateProps {
  activeWallet: WalletType;
}

interface DispatchProps {
  getWallets: typeof getWallets;
  addSigner: typeof addSigner;
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
      alert(response.address)
    } catch(error) {
      console.log(error)
    }
    this.setState({ pending: false })
  }

  render() {
    const { activeWallet } = this.props;
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

    return (
      <div>
        <h2 className='text-center'>{ activeWallet.name } ({activeWallet.m}/{activeWallet.n})</h2>
        {!activeWallet.ready && 
          <div className="text-center">Confirmed Balance: {activeWallet.balances.confirmed} BTC</div>
        }
        {activeWallet.balances.unconfirmed > 0 &&
          <div className="text-center">Unconfirmed Balance: {activeWallet.balances.unconfirmed} BTC</div>}
        {!activeWallet.ready &&
          <div className="text-center">
            <LoadingButton loading={this.state.pending} onClick={() => this.generateAddress()}>Generate Address</LoadingButton>
          </div>}
        {signersComponent}
        {addSigners}
        </div>
    )
  }
}
  
const mapStateToProps = (state: AppState) => {
  return {
    activeWallet: notNull(selectActiveWallet(state)),
  }
}

export default connect(
  mapStateToProps,
  { getWallets },
)(Wallet);
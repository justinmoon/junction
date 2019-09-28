import React from 'react';
import { connect } from 'react-redux';
import { RouteComponentProps, withRouter } from 'react-router';
import { AppState } from '../store';
import { selectActiveWallet } from '../store/wallet'
import { Wallet } from '../types';

interface StateProps {
  stateWallets: AppState['wallet']['wallets'];
  stateActiveWallet: Wallet | null;
  stateSettings: AppState['settings'];
}

interface OwnProps {
  component: React.ComponentClass | React.FunctionComponent;
  activeWallet?: boolean;
  rpc?: boolean;
}

type Props = StateProps & OwnProps & RouteComponentProps;

class RequireData extends React.Component<Props> {
  render() {
    const {
      component: Component,
      history,
      rpc,
      activeWallet,
      stateWallets,
      stateActiveWallet,
      stateSettings,
    } = this.props;

    if (rpc) {
      if (stateSettings.data && stateSettings.data.rpc.error) {
        history.replace('/settings');
        return null;
      }
      if (!stateSettings.hasLoaded) {
        return null;
      }
    }

    if (activeWallet && !stateActiveWallet) {
      if (stateWallets.hasLoaded) {
        history.replace('/create');
      }
      return null;
    }

    return <Component />;
  }
}

export default connect<StateProps, {}, OwnProps, AppState>(
  state => ({
    stateWallets: state.wallet.wallets,
    stateActiveWallet: selectActiveWallet(state),
    stateSettings: state.settings,
  }),
)(withRouter(RequireData));

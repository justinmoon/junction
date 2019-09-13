import React from 'react';
import { connect } from 'react-redux';
import { RouteComponentProps, withRouter } from 'react-router';
import { AppState } from '../store';

interface StateProps {
  stateWallets: AppState['wallet']['wallets'];
  stateActiveWallet: AppState['wallet']['activeWallet'];
  // rpcSettings
}

interface OwnProps {
  component: React.ComponentClass | React.FunctionComponent;
  activeWallet?: boolean;
  // rpc?: boolean;
}

type Props = StateProps & OwnProps & RouteComponentProps;

class RequireData extends React.Component<Props> {
  render() {
    const {
      component: Component,
      history,
      activeWallet,
      stateWallets,
      stateActiveWallet,
    } = this.props;

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
    stateActiveWallet: state.wallet.activeWallet,
  }),
)(withRouter(RequireData));

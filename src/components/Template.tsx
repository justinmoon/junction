import React from 'react';
import { connect } from 'react-redux';
import { Link, NavLink as RRNavLink } from 'react-router-dom';
import { withRouter, RouteComponentProps } from 'react-router';
import {
  Navbar,
  NavbarBrand,
  NavbarToggler,
  Container,
  Collapse,
  Nav,
  NavItem,
  NavLink,
  DropdownToggle,
  DropdownMenu,
  Spinner,
  DropdownItem,
  UncontrolledDropdown,
} from 'reactstrap';
import { getWallets, changeWallet, selectActiveWallet } from '../store/wallet';
import { startDeviceScan, stopDeviceScan } from '../store/device';
import { getSettings, validSettingsSelector } from '../store/settings';
import { bootstrap } from '../store/bootstrap'
import { AppState } from '../store';
import DeviceInstructionsModal from './DeviceInstructionsModal'
import EnterPinModal from './EnterPinModal'

interface StateProps {
  state: AppState;
  wallets: AppState['wallet']['wallets'];
  activeWallet: ReturnType<typeof selectActiveWallet>;
  hasValidSettings: boolean;
  ready: boolean;
  error: Error | null;
}

interface DispatchProps {
  getWallets: typeof getWallets;
  changeWallet: typeof changeWallet;
  startDeviceScan: typeof startDeviceScan;
  stopDeviceScan: typeof stopDeviceScan;
  getSettings: typeof getSettings;
  bootstrap: typeof bootstrap;
}

interface OwnProps {
  children: React.ReactNode;
}

type Props = StateProps & DispatchProps & OwnProps & RouteComponentProps;

interface State {
  isOpen: boolean;
}

class Template extends React.Component<Props, State> {
  state: State = {
    isOpen: false,
  };

  async componentDidMount() {
    this.props.bootstrap();
    this.props.startDeviceScan();
  }

  componentWillUnmount() {
    this.props.stopDeviceScan();
  }

  render() {

    const { wallets, activeWallet, ready, hasValidSettings } = this.props;

    // loading
    if (!ready) {
      return <div></div>
    } 
    
    // onboarding
    if (!hasValidSettings) {
      if (this.props.history.location.pathname !== '/settings') {
        this.props.history.push('/settings')
        return <div></div>
      }
    } else if (!activeWallet) {
      if (this.props.history.location.pathname !== '/create') {
        this.props.history.push('/create')
        return <div></div>
      }
    }

    const navLinks = [{
      to: '/send',
      children: 'Send',
    }, {
      to: '/settings',
      children: 'Settings',
    }, {
      to: '/history',
      children: 'History',
    }, {
      to: '/coins',
      children: 'Coins',
    }];

    if (activeWallet && activeWallet.psbts) {
      navLinks.splice(1, 0, {
        to: '/sign',
        children: 'Sign',
      });
    }

    let dropdownLabel;
    if (activeWallet) {
      dropdownLabel = activeWallet.name;
    } else if (wallets.data) {
      dropdownLabel = 'Select a Wallet';
    } else {
      dropdownLabel = <Spinner size="sm" />;
    }

    return (
      <div>
        <Navbar expand="md" color="light" light>
          <Container>
            <NavbarBrand tag={Link} to="/">
              Junction
            </NavbarBrand>
            <NavbarToggler onClick={this.toggle} />
            <Collapse isOpen={this.state.isOpen} navbar>
              <Nav className="ml-auto" navbar>
                {navLinks.map(l => (
                  <NavItem key={l.to}>
                    <NavLink
                      tag={RRNavLink}
                      activeClassName="active"
                      exact
                      {...l}
                    />
                  </NavItem>
                ))}
                <UncontrolledDropdown nav inNavbar>
                  <DropdownToggle nav caret={!!wallets.data}>
                    {dropdownLabel}
                  </DropdownToggle>
                  {wallets.data && (
                    <DropdownMenu>
                      {wallets.data.map(w => (
                        <DropdownItem
                          key={w.name}
                          onClick={() => this.props.changeWallet(w)}
                        >
                          <Link to="/">{w.name} ({w.m} of {w.n})</Link>
                        </DropdownItem>
                      ))}
                      <DropdownItem>
                        <Link to="/create">Create a New Wallet</Link>
                      </DropdownItem>
                    </DropdownMenu>
                  )}
                </UncontrolledDropdown>

              </Nav>
            </Collapse>
          </Container>
        </Navbar>
        <Container>
          {this.props.children}
        </Container>
        <DeviceInstructionsModal/>
        <EnterPinModal/>
      </div>
    );
  }

  private toggle = () => {
    this.setState({ isOpen: !this.state.isOpen });
  };
};

const mapStateToProps = (state: AppState) => {
  return {
    state: state,
    wallets: state.wallet.wallets,
    activeWallet: selectActiveWallet(state),
    hasValidSettings: validSettingsSelector(state),
    ready: state.bootstrap.ready,
    error: state.bootstrap.error,
  }
}

const ConnectedTemplate = connect<StateProps, DispatchProps, RouteComponentProps, AppState>(
  mapStateToProps,
  { getWallets, changeWallet, startDeviceScan, stopDeviceScan, getSettings, bootstrap },
)(Template);

export default withRouter(ConnectedTemplate);
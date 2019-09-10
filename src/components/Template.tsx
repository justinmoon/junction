import React from 'react';
import { connect } from 'react-redux';
import { Link, NavLink as RRNavLink } from 'react-router-dom';
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
import { getWallets, changeWallet } from '../store/wallet';
import { AppState } from '../store';

interface StateProps {
  wallets: AppState['wallet']['wallets'];
  activeWallet: AppState['wallet']['activeWallet'];
}

interface DispatchProps {
  getWallets: typeof getWallets;
  changeWallet: typeof changeWallet
}

interface OwnProps {
  children: React.ReactNode;
}

type Props = StateProps & DispatchProps & OwnProps;

interface State {
  isOpen: boolean;
}

class Template extends React.Component<Props, State> {
  state: State = {
    isOpen: false,
  };

  async componentDidMount() {
    this.props.getWallets();
  }

  render() {
    const { wallets, activeWallet } = this.props;
    const navLinks = [{
      to: '/send',
      children: 'Send',
    }, {
      to: '/sign',
      children: 'Sign',
    }];

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
                          active={w === activeWallet}
                          onClick={() => this.props.changeWallet(w)}
                        >
                          {w.name} ({w.m} of {w.n})
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
      </div>
    );
  }

  private toggle = () => {
    this.setState({ isOpen: !this.state.isOpen });
  };
};

export default connect<StateProps, DispatchProps, OwnProps, AppState>(
  state => ({
    wallets: state.wallet.wallets,
    activeWallet: state.wallet.activeWallet,
  }),
  { getWallets, changeWallet },
)(Template);

import React from 'react';
import { observer } from 'mobx-react';
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
import { connect } from '../store';
import { WalletStore } from '../store/wallet';

interface StoreProps {
  wallet: WalletStore;
}

interface OwnProps {
  children: React.ReactNode;
}

type Props = StoreProps & OwnProps;

interface State {
  isLoadingWallets: boolean;
  isOpen: boolean;
}

@observer
class Template extends React.Component<Props, State> {
  state: State = {
    isLoadingWallets: false,
    isOpen: false,
  };

  async componentDidMount() {
    try {
      this.setState({ isLoadingWallets: true });
      await this.props.wallet.getWallets();
    } catch(error) {
      alert(error.message);
    }
    this.setState({ isLoadingWallets: false });
  }

  render() {
    const { wallet } = this.props;
    const { isOpen, isLoadingWallets } = this.state;
    const navLinks = [{
      to: '/send',
      children: 'Send',
    }, {
      to: '/sign',
      children: 'Sign',
    }];

    let dropdownLabel;
    if (isLoadingWallets) {
      dropdownLabel = <Spinner size="sm" />;
    } else if (wallet.activeWallet) {
      dropdownLabel = wallet.activeWallet.name;
    } else {
      dropdownLabel = 'Select a Wallet';
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
                  <DropdownToggle nav caret>
                    {dropdownLabel}
                  </DropdownToggle>
                  <DropdownMenu>
                    {wallet.wallets.map(w => (
                      <DropdownItem
                        key={w.name}
                        active={w === wallet.activeWallet}
                        onClick={() => wallet.changeWallet(w)}
                      >
                        {w.name} ({w.m} of {w.n})
                      </DropdownItem>
                    ))}
                  </DropdownMenu>
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

export default connect(({ wallet }) => ({ wallet }))(Template);

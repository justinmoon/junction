import React from 'react';
import { connect } from 'react-redux';
import { withRouter, RouteComponentProps } from 'react-router';
import { Table } from 'reactstrap';
import { selectActiveWallet } from '../store/wallet';
import { AppState, notNull } from '../store';
import { Wallet } from '../types';
import './Send.css'

interface StateProps {
  activeWallet: Wallet;
}

type Props = StateProps & RouteComponentProps;

class Coins extends React.Component<Props> {
  render() {
    const { activeWallet } = this.props;
    return (
      <div>
        <Table>
          <thead>
            <tr>
              <th>Tx ID</th>
              <th>Output</th>
              <th>Address</th>
              <th>Confirmations</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
          {activeWallet.coins.map((tx: any, index: number) => (
            <tr>
              <td>{tx.txid}</td>
              <td>{tx.vout}</td>
              <td>{tx.address}</td>
              <td>{tx.confirmations}</td>
              <td>{tx.amount}</td>
            </tr>
          ))}
          </tbody>
        </Table>
      </div>
    );
  }
}

const ConnectedCoins = connect<StateProps, {}, RouteComponentProps, AppState>(
  state => ({
    activeWallet: notNull(selectActiveWallet(state)),
  }),
)(Coins);

export default withRouter(ConnectedCoins)

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

class History extends React.Component<Props> {
  render() {
    const { activeWallet } = this.props;
    console.log(activeWallet.history)
    return (
      <div>
        <Table>
          <thead>
            <tr>
              <th>Tx ID</th>
              <th>Address</th>
              <th>Timestamp</th>
              <th>Confirmations</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
          {activeWallet.history.map((tx: any, index: number) => (
            <tr>
              <td>{tx.txid}</td>
              <td>{tx.address}</td>
              <td>{tx.time}</td>
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

const ConnectedHistory = connect<StateProps, {}, RouteComponentProps, AppState>(
  state => ({
    activeWallet: notNull(selectActiveWallet(state)),
  }),
)(History);

export default withRouter(ConnectedHistory)

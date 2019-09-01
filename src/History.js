import React from 'react'
import { Table, Form, Button, Nav, Container, Col, Row } from 'react-bootstrap'

export default class Settings extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      error: null,
      isLoaded: false,
      txns: []
    }
  }

  componentDidMount() {
    fetch("http://localhost:5000/transactions")
      .then(res => res.json())
      .then(
        (result) => {
          console.log('result', result)
          this.setState({
            isLoaded: true,
            txns: result
          });
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  render() {
    const { error, isLoaded, txns } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {
      return (
        <Table>
          <thead>
            <tr>
              <th>Amount</th>
              <th>Confirmations</th>
              <th>Address</th>
              <th>TX ID</th>
            </tr>
          </thead>
          <tbody>
            {txns.map(txn => (
              <tr>
                <td>{txn.amount}</td>
                <td>{txn.confirmations}</td>
                <td>{txn.address}</td>
                <td>{txn.txid}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )
    }
  }
}

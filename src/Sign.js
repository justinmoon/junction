import React from 'react'
import { Table, Form, Button, Nav, Container, Col, Row } from 'react-bootstrap'

export default class Settings extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      error: null,
      isLoaded: false,
      psbt: []
    }
  }

  componentDidMount() {
    fetch("http://localhost:5000/psbt")
      .then(res => res.json())
      .then(
        (result) => {
          console.log('result', result)
          this.setState({
            isLoaded: true,
            psbt: result
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
    // FIXME: consider stealing CSS from my block-explorer to display inputs & outputs ala blockstream.info
    const { error, isLoaded, psbt } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {
      const vout = psbt['tx']['vout']
      // FIXME
      const vin = psbt['tx']['vin']
      const inputs = psbt['inputs']
      const inputsZip = vin.map(function(e, i) {
        return [e, inputs[i]['witness_utxo'] ? inputs[i]['witness_utxo'] : inputs[i]['non_witness_utxo']];
      });
      return (
        <div>
          <h4 className="text-center">Inputs</h4>
          <Table className="table-borderless">
            <tbody>
              {inputsZip.map(item => (
                <tr>
                  <td>{item[0]['txid']}:{item[0]['vout']}</td>
                  <td className="text-right">{item[1]['amount']}</td>
                </tr>
              ))}
            </tbody>
          </Table>
          <h4 className="text-center">Outputs</h4>
          <Table className="table-borderless">
            <tbody>
              {vout.map(o => (
                <tr>
                  <td>{o['scriptPubKey']['addresses'][0]}</td>
                  <td className="text-right">{o['value']}</td>
                </tr>
              ))}
              <tr>
                <td>Fee</td>
                <td className="text-right">{psbt.fee}</td>
              </tr>
            </tbody>
          </Table>
          <h4 className="text-center">Signers</h4>
          <table className="table table-borderless">
            <tbody>
              <tr>
                <td>ledger</td>
                <td className="text-right">
                  <button type="submit" className="btn btn-primary">Sign</button>
                </td>
              </tr>
              <tr>
                <td>trezor</td>
                <td className="text-right">
                  <button type="submit" className="btn btn-primary">Sign</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div className="d-flex">
            <button type="submit" className="btn btn-primary ml-auto">Broadcast</button>
          </div>
        </div>
      )
    }
  }
}

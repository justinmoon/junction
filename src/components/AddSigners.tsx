import React from 'react';
import { Button } from 'reactstrap';
import { Device } from '../types'

interface Props {
  devices: Device[];
  addSigner: (device: Device) => void;
}

export default class AddSigners extends React.Component<Props> {
  render() {
    const { devices } = this.props;

    if (!devices || !devices.length) {
      return <p>No hardware wallets detected</p>
    }

    return (
      <table>
        <thead>
          <tr>
            <th scope="col">Device</th>
            <th scope="col" className="text-right">Action</th>
          </tr>
        </thead>
        <tbody>
        {devices.map((device: Device) => 
          <tr key={device.fingerprint}>
            <td>{ device.type }</td>
            <td><Button onClick={() => this.props.addSigner(device)}>Add Signer</Button></td>
          </tr>
        )}
        </tbody>
      </table>
    )
  }
}
import React from 'react';
import { Button, Spinner } from 'reactstrap';
import { Device } from '../types'

interface Props {
  devices: Device[];
  deviceError: string;
  deviceBeingAdded: Device | null;
  addSigner: (device: Device) => void;
}

export default class AddSigners extends React.Component<Props> {
  render() {
    // FIXME: use deviceError
    const { devices, deviceBeingAdded, deviceError } = this.props;

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
            <td>
              {device !== deviceBeingAdded && <Button onClick={() => this.props.addSigner(device)}>Add Signer</Button>}
              {device === deviceBeingAdded && <Spinner size="sm"/>}
            </td>
          </tr>
        )}
        </tbody>
      </table>
    )
  }
}
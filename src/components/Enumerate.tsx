import React from 'react'
import { enumerate } from '../api'
import { Device } from '../types';

interface State {
  devices: Device[];
  isLoaded: boolean;
  error: null | Error;
}

class Enumerate extends React.Component<{}, State> {
  state: State = {
    error: null,
    isLoaded: false,
    devices: []
  };

  componentDidMount() {
    enumerate().then(
      (result) => {
        this.setState({
          isLoaded: true,
          devices: result
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
    const { error, isLoaded, devices } = this.state
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {
      return (
        <ul>
          {devices.map(device => (
            <li key={device.fingerprint}>
              {device.type} {device.fingerprint}
            </li>
          ))}
        </ul>
      );
    }
  }
}

export default Enumerate

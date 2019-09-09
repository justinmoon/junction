import React from 'react'
import { observer, connect } from '../store';
import { DeviceStore } from '../store/device';

interface StoreProps {
  device: DeviceStore;
}

type Props = StoreProps;

interface State {
  isLoading: boolean;
  error: null | Error;
}

@observer
class Enumerate extends React.Component<Props, State> {
  state: State = {
    error: null,
    isLoading: false,
  };

  async componentDidMount() {
    const { device } = this.props;
    try {
      this.setState({ isLoading: true });
      await device.getDevices();
    } catch(error) {
      this.setState({ error });
    }
    this.setState({ isLoading: false });
  }

  render() {
    const { devices } = this.props.device;
    const { error, isLoading } = this.state
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (isLoading) {
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

export default connect<StoreProps>(
  ({ device }) => ({ device })
)(Enumerate);

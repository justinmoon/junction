import React from 'react'
import { connect } from 'react-redux';
import { startDeviceScan, stopDeviceScan } from '../store/device';
import { AppState } from '../store';
import { Spinner } from 'reactstrap';

interface StateProps {
  devices: AppState['device']['devices'];
}

interface DispatchProps {
  startDeviceScan: typeof startDeviceScan;
  stopDeviceScan: typeof stopDeviceScan;
}

type Props = StateProps & DispatchProps;

class Enumerate extends React.Component<Props> {
  componentDidMount() {
    this.props.startDeviceScan();
  }

  componentWillUnmount() {
    this.props.stopDeviceScan();
  }

  render() {
    const { data, error } = this.props.devices;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (data) {
      return (
        <ul>
          {data.map(device => (
            <li key={device.fingerprint}>
              {device.type} {device.fingerprint}
            </li>
          ))}
        </ul>
      );
    } else {
      return <Spinner />;
    }
  }
}

export default connect<StateProps, DispatchProps, {}, AppState>(
  state => ({
    devices: state.device.devices,
  }),
  { startDeviceScan, stopDeviceScan },
)(Enumerate);

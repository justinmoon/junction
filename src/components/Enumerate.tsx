import React from 'react'
import { connect } from 'react-redux';
import { getDevices } from '../store/device';
import { AppState } from '../store';
import { Spinner } from 'reactstrap';

interface StateProps {
  devices: AppState['device']['devices'];
}

interface DispatchProps {
  getDevices: typeof getDevices;
}

type Props = StateProps & DispatchProps;

class Enumerate extends React.Component<Props> {
  async componentDidMount() {
    this.props.getDevices();
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
  { getDevices },
)(Enumerate);

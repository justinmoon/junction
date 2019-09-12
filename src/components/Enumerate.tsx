import React from 'react'
import { connect } from 'react-redux';
import { startDeviceScan, stopDeviceScan } from '../store/device';
import {AppState, Loadable} from '../store';
import { Spinner } from 'reactstrap';
import {Device, Wallet} from "../types";

interface StateProps {
  devices: Loadable<Device[]>;
  activeWallet: Wallet | null;
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
              {device.type} ({device.fingerprint})
              {!device.fingerprint && <button>Add Signer</button>}
            </li>
          ))}
        </ul>
      );
    } else {
      return <Spinner />;
    }
  }
}

export const mapStateToProps = (state: AppState) => {
  return {
    devices: state.device.devices,
    activeWallet: state.wallet.activeWallet
  }
};

export default connect(
 mapStateToProps,
  { startDeviceScan, stopDeviceScan },
)(Enumerate);

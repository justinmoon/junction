import React from 'react';
import { connect } from 'react-redux';
import { withRouter, RouteComponentProps } from 'react-router';
import { Form, FormGroup, Input, Label, Button } from 'reactstrap';
import { getWallets } from '../store/wallet';
import { AppState } from '../store';
import api from '../api';
import { Wallet, SendFormOutputs, SendFormOutput } from '../types';

interface DispatchProps {
  getWallets: typeof getWallets;
}

interface ConnectProps {
  // FIXME: typescript makes me accept possibility of nullness
  // How can we just demand that this not be null for the component to even load?
  activeWallet: Wallet | null;
}

type Props = DispatchProps & ConnectProps & RouteComponentProps;

interface StateProps {
  activeWallet: AppState['wallet']['activeWallet'];
}

interface LocalState {
  outputs: SendFormOutputs;
  isSubmitting: boolean;
  error: Error | null;
}

class Create extends React.Component<Props, LocalState> {
  state: LocalState = {
    outputs: [{'address': undefined, 'btc': undefined}],
    isSubmitting: false,
    error: null,
  };
  render() {
    const { outputs } = this.state;

    return (
      <Form onSubmit={this.handleSubmit}>
        {outputs.map((output, index) =>
          <div>
            <FormGroup>
              <Label>Address</Label>
              <Input
                name="address"
                value={output.address}
                placeholder="..."
                onChange={e => this.handleChange(e, index)}
              />
            </FormGroup>
            <FormGroup>
              <Label>Amount</Label>
              <Input
                name="btc"
                value={output.btc}
                type="number"
                step="0.00000001"
                placeholder="..."
                onChange={e => this.handleChange(e, index)}
              />
            </FormGroup>
          </div>
        )}
        <Button color="primary" size="lg" block onClick={this.handleAddOutput}>
          Add Output
        </Button>
        <Button color="primary" size="lg" block>
          Submit
        </Button>
      </Form>
    );
  }

  private handleChange = (ev: React.ChangeEvent<HTMLInputElement>, index: number) => {
    let { outputs } = this.state;
    let target;
    if (ev.currentTarget.name === 'btc') {
      target = Number(ev.currentTarget.value);
    } else {
      target = ev.currentTarget.value;
    }
    (outputs[index] as any)[ev.currentTarget.name] = target;
    this.setState({ outputs });
  };

  private handleAddOutput = (ev: React.FormEvent<HTMLInputElement>) => {
    let { outputs } = this.state;
    outputs.push({ address: undefined, btc: undefined });
    this.setState({ [ev.currentTarget.name]: ev.currentTarget.value } as any);
  };

  private handleSubmit = async (ev: React.FormEvent<HTMLFormElement>) => {
    ev.preventDefault();
    try {
      this.setState({ isSubmitting: true });
      const { outputs } = this.state;
      const { activeWallet } = this.props;
      await api.createPSBT({
        wallet_name: activeWallet ? activeWallet.name : '',  // FIXME
        outputs
      });
      this.props.getWallets();
      this.props.history.push('/');
    } catch(error) {
      this.setState({ error });
    }
    this.setState({ isSubmitting: false });
  };
}

const ConnectedCreate = connect<StateProps, DispatchProps, RouteComponentProps, AppState>(
  state => ({
    activeWallet: state.wallet.activeWallet,
  }),
  { getWallets },
)(Create);

export default withRouter(ConnectedCreate)

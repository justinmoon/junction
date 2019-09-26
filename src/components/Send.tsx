import React from 'react';
import { connect } from 'react-redux';
import { withRouter, RouteComponentProps } from 'react-router';
import { Form, FormGroup, Input, Label, Row, Col, Alert, Button } from 'reactstrap';
import { getWallets, selectActiveWallet } from '../store/wallet';
import { AppState } from '../store';
import api, { CreatePSBTOutput } from '../api';
import { Wallet } from '../types';
import './Send.css'
import { LoadingButton } from './Toolbox'

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
  activeWallet: Wallet | null;
}

interface LocalState {
  outputs: CreatePSBTOutput[];
  isSubmitting: boolean;
  error: Error | null;
}

class Create extends React.Component<Props, LocalState> {
  state: LocalState = {
    outputs: [{'address': undefined, 'btc': undefined}],
    isSubmitting: false,
    error: null,
  };

  private handleChangeRecipient = (ev: React.ChangeEvent<HTMLInputElement>, index: number) => {
    let { outputs } = this.state;
    (outputs[index] as any)[ev.currentTarget.name] = ev.currentTarget.value;
    this.setState({ outputs });
  };

  private handleChangeAmount = (ev: React.ChangeEvent<HTMLInputElement>, index: number) => {
    let { outputs } = this.state;
    (outputs[index] as any)[ev.currentTarget.name] = Number(ev.currentTarget.value);
    this.setState({ outputs });
  };

  private handleAddOutput = (ev: React.FormEvent<HTMLInputElement>) => {
    let { outputs } = this.state;
    outputs.push({ address: undefined, btc: undefined });
    this.setState({ [ev.currentTarget.name]: ev.currentTarget.value } as any);
  };

  private handleRemoveOutput = (index: number) => {
    let state = this.state;
    state.outputs.splice(index, 1);
    this.setState(state);
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
      this.props.history.push('/sign');
    } catch(error) {
      this.setState({ error: error.message });
    }
    this.setState({ isSubmitting: false });
  };

  render() {
    const { outputs, error } = this.state;
    return (
      <div className="center-block">
        {error && (
          <Alert className="mb-1" color="danger">{error}</Alert>
        )}
        <Form onSubmit={this.handleSubmit}>
        {outputs.map((output, index) =>
          <div key={index}>
            <Row>
              <Col xs="8">
                <FormGroup>
                  <Label>Recipient Address</Label>
                  <Input
                    name="address"
                    value={output.address}
                    placeholder="Recipient Address"
                    onChange={e => this.handleChangeRecipient(e, index)}
                  />
                </FormGroup>
              </Col>
              <Col xs="3">
                <FormGroup>
                  <Label>Amount in BTC</Label>
                  <Input
                    name="btc"
                    value={output.btc}
                    type="number"
                    step="0.00000001"
                    placeholder="Amount in BTC"
                    onChange={e => this.handleChangeAmount(e, index)}
                  />
                </FormGroup>
              </Col>
              <Col xs="1">
                <Button color="danger" className="remove" 
                  disabled={outputs.length === 1} onClick={() => this.handleRemoveOutput(index)}>
                  X
                </Button>
              </Col>
            </Row>
            <hr/>
          </div>
        )}
        <div className="d-flex">
          <Button color="secondary" className="ml-auto m-2" onClick={this.handleAddOutput}>
            Add Output
          </Button>
          <LoadingButton loading={this.state.isSubmitting} color="primary" className="m-2">
            Submit
          </LoadingButton>
        </div>
      </Form>
      </div>
    );
  }
}

const ConnectedCreate = connect<StateProps, DispatchProps, RouteComponentProps, AppState>(
  state => ({
    activeWallet: selectActiveWallet(state),
  }),
  { getWallets },
)(Create);

export default withRouter(ConnectedCreate)

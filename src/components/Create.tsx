import React from 'react';
import { connect } from 'react-redux';
import { withRouter, RouteComponentProps } from 'react-router';
import { Form, FormGroup, Input, Label, Col, Row, Alert } from 'reactstrap';
import { getWallets, changeWallet } from '../store/wallet';
import { getNodes } from '../store/node';
import { LoadingButton } from './Toolbox'
import api from '../api';
import { AppState, notNull } from '../store';

interface DispatchProps {
  getWallets: typeof getWallets;
  changeWallet: typeof changeWallet;
  getNodes: typeof getNodes;
}

interface StateProps {
  bitcoinNodes: any[];  // FIXME
  changeWallet: typeof changeWallet;
}

type Props = StateProps & DispatchProps & RouteComponentProps;

interface State {
  // form: T.CreateWalletArguments,
  form: {
    name: string;
    m: string;
    n: string;
    network: string;
    wallet_type: string;
    script_type: string;
    node: {
      user: string;
      password: string;
      host: string;
      port: string;
    }
  }
  isSubmitting: boolean;
  error: Error | null;
  interval: any;
}

function sameNode(a: any, b: any) {
  return a.host === b.host &&
         a.port === b.port &&
         a.user === b.user &&
         a.password === b.password;
}

class Create extends React.Component<Props, State> {
  state: State = {
    form: {
      name: '',
      m: '',
      n: '',
      network: '',
      wallet_type: '',
      script_type: '',
      node: {
        user: '',
        password: '',
        host: '',
        port: '',
      }
    },
    isSubmitting: false,
    error: null,
    interval: null,
  };

  componentWillMount() {
    const interval = setInterval(() => {
      this.props.getNodes()
    }, 1000);
    this.setState({ interval })
  }

  componentWillUnmount() {
    clearInterval(this.state.interval);
  }

  renderNodeForm() {
    const fields: {
      label: React.ReactNode;
      name: keyof State["form"]["node"];
      type: string;
      placeholder: string;
    }[] = [{
      label: 'RPC Username (Optional)',
      name: 'user',
      type: 'text',
      placeholder: 'satoshi',
    }, {
      label: 'RPC Password (Optional)',
      name: 'password',
      type: 'password',
      placeholder: '**********',
    }, {
      label: 'RPC Hostname',
      name: 'host',
      type: 'text',
      placeholder: '127.0.0.1',
    }, {
      label: 'RPC Port',
      name: 'port',
      type: 'text',
      placeholder: '18332',
    }];

    return fields.map(f => (
      <FormGroup key={f.name}>
        <Label>{f.label}</Label>
        <Input
          name={f.name}
          // type={f.type}  // FIXME
          value={this.state.form.node[f.name]}
          placeholder={f.placeholder}
          onChange={this.handleChange}
        />
      </FormGroup>
    ))
  }

  render() {
    const { bitcoinNodes } = this.props;
    const { form, isSubmitting } = this.state;
    return (
      <Form onSubmit={this.handleSubmit}>
        <h4 className="text-center">Setup Wallet</h4>
        <FormGroup>
          <Label>Wallet Name</Label>
          <Input
            name="name"
            value={form.name}
            placeholder=""
            onChange={this.handleChange}
          />
          <Row className="pt-3">
            <Col xs="4">
              <FormGroup>
                <Label>Wallet Type</Label>
                <br/>
                <Input addon type="radio" 
                  checked={form.wallet_type === 'single'}
                  onChange={() => this.setKey({'wallet_type': 'single', 'm': '1', 'n': '1'})}/> Single-signature
                <br/>
                <Input addon type="radio" 
                  checked={form.wallet_type === 'multi'}
                  onChange={() => this.setKey({'wallet_type': 'multi'})}/> Multi-signature
              </FormGroup>
            </Col>
            <Col xs="4">
              <FormGroup>
                <Label>Script Type</Label>
                <br/>
                <Input addon type="radio" 
                  checked={form.script_type === 'native'}
                  onChange={() => this.setKey({'script_type': 'native'})}/> Native Segwit
                <br/>
                <Input addon type="radio" 
                  checked={form.script_type === 'wrapped'}
                  onChange={() => this.setKey({'script_type': 'wrapped'})}/> Wrapped Segwit
              </FormGroup>
            </Col>
            <Col xs="4">
              <FormGroup>
                <Label>Choose Network</Label>
                <br/>
                <Input name="mainnet" addon type="radio" 
                  checked={this.state.form.network == "mainnet"}
                  onChange={() => this.setKey({'network': 'mainnet'})}/> Mainnet (real bitcoins)
                <br/>
                <Input name="testnet" addon type="radio"
                  checked={this.state.form.network == "testnet"}
                  onChange={() => this.setKey({'network': 'testnet'})}/> Testnet (for testing)
              </FormGroup>
            </Col>
          </Row>
          {form.wallet_type === 'multi' && <Row>
            <Col xs="6">
              <Label>Signatures Required</Label>
              <Input
                name="m"
                value={form.m}
                placeholder=""
                onChange={this.handleChange}
              />
            </Col>
            <Col xs="6">
              <Label>Total Number of Signers</Label>
              <Input
                name="n"
                value={form.n}
                placeholder=""
                onChange={this.handleChange}
              />
            </Col>
          </Row>}
        </FormGroup>
        {this.setupComplete() && <div>
          <h4 className="text-center">Connect to Bitcoin Node</h4>
          <Row>
            <Col xs="6">
              {bitcoinNodes.map((node: any, index: number) => {
                if (node.network == this.state.form.network) {
                  return (
                    <FormGroup>
                      <Label><i>Nodes Detected Locally</i></Label>
                      <br/>
                      <Input addon type="radio" 
                        checked={sameNode(node, this.state.form.node)}
                        onChange={() => this.chooseNode(node)}/> {node.host}:{node.port}
                    </FormGroup>
                  )
                }
              })}
            </Col>
            <Col xs="6">
              <FormGroup>
                <p><i>Or Connect to Another Node via RPC</i></p>
                <Label>RPC Hostname</Label>
                <Input name="host" type="text" onChange={this.handleNodeChange}/>
                <Label>RPC Port</Label>
                <Input name="port" type="text" onChange={this.handleNodeChange}/>
                <Label>RPC User</Label>
                <Input name="user" type="text" onChange={this.handleNodeChange}/>
                <Label>RPC Password</Label>
                <Input name="password" type="text" onChange={this.handleNodeChange}/>
              </FormGroup>
            </Col>
          </Row>
        </div>}
        {this.state.error && <Alert color="danger">{this.state.error}</Alert>}
        <LoadingButton disabled={!this.formComplete()} color="primary" size="lg" block loading={isSubmitting}>
          Submit
        </LoadingButton>
      </Form>
    );
  }

  private chooseNode = (node: any) => {
    let stateNode;
    if (sameNode(node, this.state.form.node)) {
      stateNode = {
        host: '',
        port: '',
        user: '',
        password: '',
      }
    } else {
      stateNode = {
        host: node.host,
        port: node.port,
        user: node.user,
        password: node.password,
      }
    }

    this.setState({ 
      form: {
        ...this.state.form,
        node: stateNode,
      },
    });
  };

  private setupComplete = () => {
    const { form } = this.state;
    const keys = Object.values(form)
    return keys.indexOf('') === -1
  };

  private formComplete = () => {
    const { form } = this.state;
    const nodeKeys = Object.values(form.node)
    const nodeComplete = nodeKeys.indexOf('') === -1
    return this.setupComplete() && nodeComplete; 
  };

  private setKey = (obj: Object) => {
    this.setState({ 
      form: { ...this.state.form, ...obj } as any,
    });
  };

  private handleChange = (ev: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ 
      form: {
        ...this.state.form, 
        [ev.currentTarget.name]: ev.currentTarget.value 
      },
    });
  };

  private handleNodeChange = (ev: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ 
      form: {
        ...this.state.form, 
        node: {
          ...this.state.form.node,
          [ev.currentTarget.name]: ev.currentTarget.value
        }
      },
    });
  };

  private handleSubmit = async (ev: React.FormEvent<HTMLFormElement>) => {
    ev.preventDefault();
    try {
      this.setState({ isSubmitting: true });
      
      const wallet = await api.createWallet({
        ...this.state.form,
        m: parseInt(this.state.form.m, 10),
        n: parseInt(this.state.form.n, 10),
      });
      await this.props.getWallets();
      this.props.changeWallet(wallet);
      this.props.history.push('/');
    } catch(error) {
      this.setState({ error: error.message });
    }
    this.setState({ isSubmitting: false });
  };
}

const mapStateToProps = (state: AppState) => {
  return {
    bitcoinNodes: notNull(state.node.data && state.node.data.bitcoin),  // FIXME
  }
}
const ConnectedCreate = connect<{}, DispatchProps, RouteComponentProps, AppState>(
  mapStateToProps,
  { getWallets, changeWallet, getNodes },
)(Create);

export default withRouter(ConnectedCreate)

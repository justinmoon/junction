import React from 'react';
import { connect } from 'react-redux';
import { withRouter, RouteComponentProps } from 'react-router';
import { Form, FormGroup, Input, Label, Col, Row, Alert } from 'reactstrap';
import { getWallets, changeWallet } from '../store/wallet';
import { getNodes } from '../store/node';
import { LoadingButton } from './Toolbox'
import api from '../api';
import { AppState, notNull } from '../store';
import { sleep } from '../util';

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
  isScanning: boolean;
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
    isScanning: false,
  };

  componentWillMount() {
    this.startScan()
  }

  async startScan() {
    await this.setState({ isScanning: true })
    while (this.state.isScanning) {
      console.log(this.state.isScanning)
      try {
        await this.props.getNodes()
      } catch (e) {
        console.log('Failed to fetch nodes')
      }
      await sleep(3000);
    }
  }

  componentWillUnmount() {
    this.setState({ isScanning: false })
  }

  private selectTestnet = (e: any) => {
    this.setKey({'network': 'testnet', 'node': { ...this.state.form.node, port: '18332' }})

  };

  private selectMainnet = (e: any) => {
    this.setKey({'network': 'mainnet', 'node': { ...this.state.form.node, port: '8332' }})
  }

  private selectSingleSig = (e: any) => {
    this.setKey({'wallet_type': 'single', 'm': '1', 'n': '1'})  }

  private selectMultiSig = (e: any) => {
    this.setKey({'wallet_type': 'multi', 'm': '', 'n': ''})
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
            <Col xs="6">
              <FormGroup>
                <Label>Wallet Type</Label>
                <br/>
                <Input addon type="radio" 
                  checked={form.wallet_type === 'single'}
                  onChange={this.selectSingleSig}/>
                <span onClick={this.selectSingleSig}> Single-Signature</span>
                <br/>
                <Input addon type="radio" 
                  checked={form.wallet_type === 'multi'}
                  onChange={this.selectMultiSig}/>
                <span onClick={this.selectMultiSig}> Multi-Signature</span>
              </FormGroup>
            </Col>
            <Col xs="6">
              <FormGroup>
                <Label>Choose Network</Label>
                <br/>
                <Input name="mainnet" addon type="radio" 
                  checked={this.state.form.network == "mainnet"}
                  onChange={this.selectMainnet}/>
                <span onClick={this.selectMainnet}> Mainnet (real bitcoins)</span>
                <br/>
                <Input name="testnet" addon type="radio"
                  checked={this.state.form.network == "testnet"}
                  onChange={this.selectTestnet}/>
                  <span onClick={this.selectTestnet}> Testnet (for testing)</span>
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
             <FormGroup>
              <Label><i>Nodes Detected Locally</i></Label>
              {bitcoinNodes.map((node: any, index: number) => {
                if (node.network == this.state.form.network) {
                  return (
                    <div>
                      <br/>
                      <Input addon type="radio" 
                        checked={sameNode(node, this.state.form.node)}
                        onChange={() => this.chooseNode(node)}/>
                        <span onClick={() => this.chooseNode(node)}> {node.host}:{node.port}</span>
                    </div>
                  )
                }
              })}
              </FormGroup>
            </Col>
            <Col xs="6">
              <FormGroup>
                <p><i>Or Connect to Another Node via RPC</i></p>
                <Label>RPC Hostname</Label>
                <Input name="host" type="text" value={form.node.host} onChange={this.handleNodeChange}/>
                <Label>RPC Port</Label>
                <Input name="port" type="text" value={form.node.port} onChange={this.handleNodeChange}/>
                <Label>RPC User</Label>
                <Input name="user" type="text" value={form.node.user} onChange={this.handleNodeChange}/>
                <Label>RPC Password</Label>
                <Input name="password" type="password" value={form.node.password} onChange={this.handleNodeChange}/>
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
    let payload = {
      ...this.state.form,
      m: parseInt(this.state.form.m, 10),
      n: parseInt(this.state.form.n, 10),
    }
    delete payload.wallet_type
    try {
      this.setState({ isSubmitting: true });
      
      const wallet = await api.createWallet(payload);
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

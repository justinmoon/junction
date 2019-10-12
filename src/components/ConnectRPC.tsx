import React from 'react';
import { Button, Modal, ModalHeader, ModalFooter, ModalBody, Form, Alert, FormGroup, Label, Input } from 'reactstrap';
import { AppState } from '../store';
import { toggleDeviceInstructionsModal } from '../store/modal'
import { connect } from 'react-redux';
import { selectActiveWallet, getWallets } from '../store/wallet';
import {  Wallet } from '../types';
import { LoadingButton } from './Toolbox';
import api from '../api';

interface DispatchProps {
  toggleDeviceInstructionsModal: typeof toggleDeviceInstructionsModal;
  getWallets: typeof getWallets;
}

interface StateProps {
  activeWallet: Wallet | null;
}

type Props = DispatchProps & StateProps

type State = {
  host: string;
  port: string;
  user: string;
  password: string;
  authenticating: boolean;
  syncing: boolean;
  error: string;
  dirty: boolean;
}

class DeviceInstructionsModal extends React.Component<Props> {
  state: State = {
    host: '',
    port: '',
    user: '',
    password: '',
    authenticating: false,
    syncing: false,
    error: '',
    dirty: false,
  }

  private handleChange = (ev: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ [ev.currentTarget.name]: ev.currentTarget.value, dirty: true });
  };

  private handleUpdateNode = async (ev: React.FormEvent<HTMLFormElement>) => {
    ev.preventDefault();
    if (this.props.activeWallet) {
      this.setState({ authenticating: true })
      try {
        await api.updateNode({
          wallet_name: this.props.activeWallet.name,
          host: this.state.host,
          port: this.state.port,
          user: this.state.user,
          password: this.state.password,
        });
      } catch(error) {
        this.setState({ authenticating: false, error: error.message })
        return
      }
      await this.props.getWallets()
      this.setState({ authenticating: false, host: '', port: '', user: '', password: '', dirty: false })
    }
  };
  
  private handleSync = async (ev: React.FormEvent<HTMLFormElement>) => {
    if (this.props.activeWallet) {
      this.setState({ syncing: true })
      try {
        await api.sync({
          wallet_name: this.props.activeWallet.name,
        });
      } catch(error) {
        this.setState({ syncing: false, error: error.message })
        return
      }
      await this.props.getWallets()
      this.setState({ syncing: false })
    }
  };
  

  static getDerivedStateFromProps(props: any, state: State) {
    if (props.activeWallet && !state.dirty) {
      const node = props.activeWallet.node
      return {
        ...state,
        host: node.host,
        port: node.port,
        user: node.user,
        password: node.password,
      }
    }
    return state
  }

  render() {
    const { activeWallet } = this.props;
    if (!activeWallet) {
      return <div></div>
    }
    const rpcError = activeWallet.node.rpc_error
    const hasRpcError = !!rpcError
    const authError = rpcError && rpcError.includes('credentials')
    const notSynced = activeWallet.synced === false
    const showModal = hasRpcError || notSynced
    return (
			<Modal isOpen={showModal}>
				<ModalHeader>Node Connection Problem</ModalHeader>
				<ModalBody>
          {hasRpcError && <div>
            <Alert className="mb-1" color="danger">{this.state.error || rpcError}</Alert>
          <Form onSubmit={this.handleUpdateNode}>
            {authError && <div>
              <FormGroup>
                <Label>RPC Hostname</Label>
                <Input name="host" type="text" value={this.state.host} onChange={this.handleChange}/>
                <Label>RPC Port</Label>
                <Input name="port" type="text" value={this.state.port} onChange={this.handleChange}/>
                <Label>RPC User</Label>
                <Input name="user" type="text" value={this.state.user} onChange={this.handleChange}/>
                <Label>RPC Password</Label>
                <Input name="password" type="password" value={this.state.password} onChange={this.handleChange}/>
              </FormGroup>
              <LoadingButton loading={this.state.authenticating} color="primary" size="lg" block>
                Connect
              </LoadingButton>
            </div>}
            </Form>            
          </div>}
          {!hasRpcError && notSynced && <div>
            Your Bitcoin node is out-of-sync with Junction<br/>
            <LoadingButton loading={this.state.syncing} onClick={this.handleSync} color="primary" size="lg" block>
                Sync Node
            </LoadingButton>
          </div>}
				</ModalBody>
			</Modal>
		)
	}
}

export const mapStateToProps = (state: AppState) => {
	return {
    activeWallet: selectActiveWallet(state),
	}
}
  
export default connect(
	mapStateToProps,
	{ toggleDeviceInstructionsModal, getWallets },
)(DeviceInstructionsModal);
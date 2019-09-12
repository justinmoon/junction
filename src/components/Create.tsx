import React from 'react';
import { connect } from 'react-redux';
import { withRouter, RouteComponentProps } from 'react-router';
import { Form, FormGroup, Input, Label, Button } from 'reactstrap';
import { getWallets, changeWallet } from '../store/wallet';
import api from '../api';

interface DispatchProps {
  getWallets: typeof getWallets;
  changeWallet: typeof changeWallet;
}

type Props = DispatchProps & RouteComponentProps;

interface State {
  name: string;
  m: string;
  n: string;
  isSubmitting: boolean;
  error: Error | null;
}

class Create extends React.Component<Props, State> {
  state: State = {
    name: '',
    m: '',
    n: '',
    isSubmitting: false,
    error: null,
  };

  render() {
    const { name, m, n } = this.state;

    return (
      <Form onSubmit={this.handleSubmit}>
        <FormGroup>
          <Label>Name</Label>
          <Input
            name="name"
            value={name}
            placeholder="Cold storage"
            onChange={this.handleChange}
          />
        </FormGroup>
        <FormGroup>
          <Label>Number of Signers</Label>
          <Input
            name="n"
            value={n}
            placeholder="5"
            onChange={this.handleChange}
          />
        </FormGroup>
        <FormGroup>
          <Label>Signers Required</Label>
          <Input
            name="m"
            value={m}
            placeholder="3"
            onChange={this.handleChange}
          />
        </FormGroup>
        <Button color="primary" size="lg" block>
          Submit
        </Button>
      </Form>
    );
  }

  private handleChange = (ev: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ [ev.currentTarget.name]: ev.currentTarget.value } as any);
  };

  private handleSubmit = async (ev: React.FormEvent<HTMLFormElement>) => {
    ev.preventDefault();
    try {
      this.setState({ isSubmitting: true });
      const { name, m, n } = this.state;
      const wallet = await api.createWallet({
        name,
        m: parseInt(m, 10),
        n: parseInt(n, 10),
      });
      await this.props.getWallets();
      this.props.changeWallet(wallet);
      this.props.history.push('/');
    } catch(error) {
      this.setState({ error });
    }
    this.setState({ isSubmitting: false });
  };
}

const ConnectedCreate = connect<{}, DispatchProps, RouteComponentProps, {}>(
  undefined,
  { getWallets, changeWallet },
)(Create);

export default withRouter(ConnectedCreate)

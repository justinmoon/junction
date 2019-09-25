import React from 'react';
import { connect } from 'react-redux';
import { Form, FormGroup, Input, Label, Button, Alert, Spinner } from 'reactstrap';
import { withRouter, RouteComponentProps } from 'react-router';
import { getSettings, updateSettings, Settings as TSettings } from '../store/settings';
import { AppState } from '../store';

interface StateProps {
  settings: AppState['settings'];
}

interface DispatchProps {
  getSettings: typeof getSettings;
  updateSettings: typeof updateSettings;
}

type Props = StateProps & DispatchProps & RouteComponentProps;

type State = TSettings['rpc'];

class Settings extends React.Component<Props> {
  state: State = {
    user: '',
    password: '',
    host: '',
    port: '',
  }

  componentDidMount() {
    const { settings } = this.props;
    if (!settings.data && !settings.isLoading) {
      this.props.getSettings();
    } else if (settings.data) {
      this.setState({ ...settings.data.rpc });
    }
  }

  componentDidUpdate(prevProps: Props) {
    const { settings } = this.props;
    if (settings.data && settings.data !== prevProps.settings.data) {
      this.setState({ ...settings.data.rpc });
    }
  }

  render() {
    const { settings } = this.props;
    
    const fields: {
      label: React.ReactNode;
      name: keyof State;
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

    let error;
    if (settings.error) {
      error = settings.error.message;
    } else if (settings.data && settings.data.rpc.error) {
      error = settings.data.rpc.error;
    }

    return (
      <Form onSubmit={this.handleSubmit}>
        {error && (
          <Alert className="mb-1" color="danger">{error}</Alert>
        )}
        {fields.map(f => (
          <FormGroup key={f.name}>
            <Label>{f.label}</Label>
            <Input
              name={f.name}
              // type={f.type}  // FIXME
              value={this.state[f.name]}
              placeholder={f.placeholder}
              onChange={this.handleChange}
            />
          </FormGroup>
        ))}
        <Button color="primary" size="lg" block>
          Save
        </Button>
      </Form>
    )
  }

  private handleChange = (ev: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ [ev.currentTarget.name]: ev.currentTarget.value });
  };

  private handleSubmit = (ev: React.FormEvent<HTMLFormElement>) => {
    ev.preventDefault();
    this.props.updateSettings({
      rpc: { ...this.state },
    });
  };
}

export default withRouter(connect<StateProps, DispatchProps, RouteComponentProps, AppState>(
  state => ({ 
    settings: state.settings,
  }),
  { getSettings, updateSettings },
)(Settings));

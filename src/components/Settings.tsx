import React from 'react';
import { connect } from 'react-redux';
import { Form, FormGroup, Input, Label, Button, Alert, Spinner } from 'reactstrap';
import { getSettings, updateSettings, Settings as TSettings } from '../store/settings';
import { AppState } from '../store';

interface StateProps {
  settings: AppState['settings'];
}

interface DispatchProps {
  getSettings: typeof getSettings;
  updateSettings: typeof updateSettings;
}

type Props = StateProps & DispatchProps;

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
    if (!settings.hasLoaded) {
      return <Spinner />;
    }

    const fields: {
      label: React.ReactNode;
      name: keyof State;
      placeholder: string;
    }[] = [{
      label: 'RPC Username (Optional)',
      name: 'user',
      placeholder: 'satoshi',
    }, {
      label: 'RPC Password (Optional)',
      name: 'password',
      placeholder: '**********',
    }, {
      label: 'RPC Hostname',
      name: 'host',
      placeholder: '127.0.0.1',
    }, {
      label: 'RPC Port',
      name: 'port',
      placeholder: '18332',
    }];

    let error;
    if (settings.error) {
      error = settings.error;
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
    // return JSON.stringify(this.props.settings);
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

export default connect<StateProps, DispatchProps, {}, AppState>(
  state => ({ settings: state.settings }),
  { getSettings, updateSettings },
)(Settings);

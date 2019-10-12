import React from 'react';
import { HashRouter } from 'react-router-dom';
import { Switch, Route } from 'react-router';
import Template from './components/Template';
import Wallet from './components/Wallet';
import Send from './components/Send';
import Sign from './components/Sign';
import History from './components/History';
import Create from './components/Create';
import ErrorScreen from './components/ErrorScreen';
import Coins from './components/Coins';

interface State {
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

export default class App extends React.Component<{}, State> {
  state: State = {
    error: null,
    errorInfo: null,
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    (window as any).__reactCaughtError = true;
    this.setState({ error, errorInfo });
  }

  render() {
    const { error, errorInfo } = this.state;
    if (error) {
      return <ErrorScreen error={error} errorInfo={errorInfo} />;
    }

    return (
      <HashRouter>
        <Switch>
          <Template>
            <Route path="/" exact component={Wallet} />
            <Route path="/send" component={Send}/>
            <Route path="/sign" component={Sign}/>
            <Route path="/history" component={History}/>
            <Route path="/create" component={Create}/>
            <Route path="/coins" component={Coins} />
          </Template>
        </Switch>
      </HashRouter>
    );
  }
}

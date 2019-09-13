import React from 'react';
import { HashRouter } from 'react-router-dom';
import { Switch, Route } from 'react-router';
import Template from './components/Template';
import Wallet from './components/Wallet';
import Send from './components/Send';
import Sign from './components/Sign';
import History from './components/History';
import Create from './components/Create';
import RequireData from './components/RequireData';

const App: React.FC = () => {
  return (
    <HashRouter>
      <Template>
        <Switch>
          <Route path="/" exact render={() => (
            <RequireData activeWallet component={Wallet} />
          )} />
          <Route path="/send" render={() => (
            <RequireData activeWallet component={Send} />
          )} />
          <Route path="/sign" render={() => (
            <RequireData activeWallet component={Sign} />
          )} />
          <Route path="/history" render={() => (
            <RequireData activeWallet component={History} />
          )} />
          <Route path="/create" component={Create} />
        </Switch>
      </Template>
    </HashRouter>
  );
}

export default App;

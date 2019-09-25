import React from 'react';
import { HashRouter } from 'react-router-dom';
import { Switch, Route } from 'react-router';
import Template from './components/Template';
import Wallet from './components/Wallet';
import Send from './components/Send';
import Sign from './components/Sign';
import History from './components/History';
import Create from './components/Create';
import Settings from './components/Settings';
import RequireData from './components/RequireData';

const App: React.FC = () => {
  return (
    <HashRouter>
      <Switch>
        <Template>
            <Route path="/" exact render={() => (
              <RequireData rpc activeWallet component={Wallet} />
            )} />
            <Route path="/send" render={() => (
              <RequireData rpc activeWallet component={Send} />
            )} />
            <Route path="/sign" render={() => (
              <RequireData rpc activeWallet component={Sign} />
            )} />
            <Route path="/history" render={() => (
              <RequireData rpc activeWallet component={History} />
            )} />
            <Route path="/create" render={() => (
              <RequireData rpc component={Create} />
            )} />
            <Route path="/settings" component={Settings} />
        </Template>
      </Switch>
    </HashRouter>
  );
}

export default App;
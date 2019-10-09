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
import Coins from './components/Coins';

const App: React.FC = () => {
  return (
    <HashRouter>
      <Switch>
        <Template>
            <Route path="/" exact component={Wallet} />
            <Route path="/send" component={Send}/>
            <Route path="/sign" component={Sign}/>
            <Route path="/history" component={History}/>
            <Route path="/create" component={Create}/>
            <Route path="/settings" component={Settings} />
            <Route path="/coins" component={Coins} />
        </Template>
      </Switch>
    </HashRouter>
  );
}

export default App;
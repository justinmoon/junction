import React from 'react';
import { HashRouter } from 'react-router-dom';
import { Switch, Route } from 'react-router';
import Template from './components/Template';
import Home from './components/Home';
import Send from './components/Send';
import Sign from './components/Sign';
import History from './components/History';
import Create from './components/Create';

const App: React.FC = () => {
  return (
    <HashRouter>
      <Template>
        <Switch>
          <Route path="/" exact component={Home} />
          <Route path="/send" component={Send} />
          <Route path="/sign" component={Sign} />
          <Route path="/history" component={History} />
          <Route path="/create" component={Create} />
        </Switch>
      </Template>
    </HashRouter>
  );
}

export default App;

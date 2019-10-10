import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import App from './App';
import ErrorScreen from './components/ErrorScreen';
import * as serviceWorker from './serviceWorker';
import { makeStore } from './store';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';

const store = makeStore();
const root = document.getElementById('root') as HTMLElement;

ReactDOM.render(
  (
    <Provider store={store}>
      <App />
    </Provider>
  ),
  root,
);

// Render uncaught errors. App's componentDidCatch might handle the errors shortly,
// so don't jump the gun on it. Check if it set the window marker.
function renderErrorScreen(error: Error) {
  setTimeout(() => {
    if (!(window as any).__reactCaughtError) {
      ReactDOM.render(<ErrorScreen error={error} />, root);
    }
  }, 100);
}
window.addEventListener('error', (ev: ErrorEvent) => {
  renderErrorScreen(ev.error);
});
window.addEventListener('unhandledrejection', (ev: PromiseRejectionEvent) => {
  renderErrorScreen(ev.reason);
});

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();

import { createStore, applyMiddleware, Store, Middleware } from 'redux';
import thunk from 'redux-thunk';
import { createLogger } from 'redux-logger';
import { composeWithDevTools } from 'redux-devtools-extension';
import { AppState, rootReducer } from './reducers';

export function makeStore() {
  const middleware: Middleware[] = [thunk];
  if (process.env.NODE_ENV !== 'production') {
    middleware.push(createLogger({ collapsed: true }));
  }

  const store: Store<AppState> = createStore(
    rootReducer,
    undefined,
    composeWithDevTools(applyMiddleware(...middleware)),
  )
  return store;
}

import { inject } from 'mobx-react';
import { InferableComponentEnhancerWithProps } from 'react-redux';
import { WalletStore } from './wallet';
import { DeviceStore } from './device';

export function createStore() {
  const wallet = new WalletStore();
  const device = new DeviceStore();
  return { wallet, device };
}

// Here we're wrapping mobx's inject method to allow for strong typing
// The goal here is to do two things:
// 1) Not use inject's string arguments, which are virtually untypable
// 2) Allow React components to specify which props come from mobx, and
//    which props they need passed.
// This uses some of @types/react-redux's handy typing, because that module
// has way better typing.
// Source: https://github.com/mobxjs/mobx-react/issues/256#issuecomment-496294124
type MapStoresToProps<InjectedProps, OwnProps> = (
  state: ReturnType<typeof createStore>,
  ownProps: OwnProps,
) => InjectedProps;

export function connect<InjectedProps extends object, OwnProps extends object = {}>(
  fn: MapStoresToProps<InjectedProps, OwnProps>
) {
  return inject(fn) as InferableComponentEnhancerWithProps<InjectedProps, OwnProps>;
}

// Convenience export for components, so they only need to import one file
// for all their mobx component needs.
export { action } from 'mobx';
export { observer } from 'mobx-react';
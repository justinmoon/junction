import React from 'react';
import { Button, Modal, ModalHeader, ModalFooter, ModalBody, Spinner } from 'reactstrap';
import api from '../api'
import './EnterPinModal.css';
import { AppState } from '../store';
import { connect } from 'react-redux';
import { toggleDeviceUnlockModal } from '../store/modal'
import { LoadingButton } from './Toolbox';


const digits = [
  [7,8,9],
  [4,5,6],
  [1,2,3],
]

interface StateProps {
  open: boolean;
}

interface DispatchProps {
  // toggleDeviceUnlockModal: typeof toggleDeviceUnlockModal;
  toggleDeviceUnlockModal: any;  // FIXME
}

type Props = StateProps & DispatchProps

interface State {
  pin: string;
  pending: boolean;
  error: string | null;
  pressed: number | null;
}

// TODO: move to redux?
const initialState = {
  pin: '',
  pending: false,
  error: null,
  pressed: null,
};

class EnterPinModal extends React.Component<Props, State> {
  state: State = initialState;

  async enterPin() {
    const { pin, pending } = this.state;
    if (!pending) {
      try {
        this.setState({ pending: true })
        await api.enterPin({ pin });
        this.toggle()
      } catch(error) {
        this.setState({ 
          error: error.message,
          pin: '',
          pending: false,
         });
        setTimeout(api.promptPin, 1000);
      }
    }
  }

  // FIXME: does this help?
  // async componentWillUnmount() {
  //   await api.deletePrompt()
  // }

  handlePinClick(digit: number) {
    if (!this.state.pending) {
      this.setState({ pin: this.state.pin + String(digit) });
    }
  }

  backspace() {
    if (!this.state.pending) {
      const oldPin = this.state.pin
      if (oldPin.length > 0) {
        const pin = oldPin.substring(0, oldPin.length - 1);
        this.setState({ pin });
      }
    }
  }

  renderPin() {
    const { pin } = this.state;
    return (
      <div className="PinModal-pins">
        {digits.map((row, idx) => (
          <div className="PinModal-pins-row" key={idx}>
            {row.map((digit) => (
              <div
                className="PinModal-pins-pin"
                key={digit}
                onClick={() => this.handlePinClick(digit)}
              />
            ))}
          </div>
        ))}
        <div>PIN: {"•".repeat(pin.length)}</div>
      </div>
    )
  }

  toggle() {
    this.setState(initialState)
    this.props.toggleDeviceUnlockModal();
  }

  // handleClosed() {
  //   api.deletePrompt();
  // }

  // componentWillUnmount() {
  //   this.handleClosed();
  // }

  renderError() {
    const style = {
      color: 'red',
    } 
    const { error } = this.state;
    if (error) {
      return <div style={style}>{error}</div>
    }
  }

  renderFooter() {
    const { pending } = this.state;
    return (
      <ModalFooter>
        {this.renderError()}
        <Button color="danger" onClick={this.backspace.bind(this)}>
          Backspace
        </Button>
        <LoadingButton loading={pending} color="secondary" onClick={this.enterPin.bind(this)}>
          Submit
        </LoadingButton>
      </ModalFooter>
    )
  }

  render() {
    const { open } = this.props;
    return (
			<Modal isOpen={open} toggle={this.toggle.bind(this)} className="PinModal">
				<ModalHeader toggle={this.toggle.bind(this)}>EnterPin</ModalHeader>
				<ModalBody>
          {this.renderPin()}
				</ModalBody>
        {this.renderFooter()}
			</Modal>
		)
	}
}

export const mapStateToProps = (state: AppState) => {
  return {
    open: state.modal.deviceUnlock.open,
  }
}

export default connect(
  mapStateToProps,
  { toggleDeviceUnlockModal },
)(EnterPinModal);
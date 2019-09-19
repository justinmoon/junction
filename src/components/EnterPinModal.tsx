import React from 'react';
import { Button, Modal, ModalHeader, ModalFooter, ModalBody, Row, Spinner } from 'reactstrap';
import api from '../api'
import { Device } from '../types';
import './EnterPinModal.css';
import { AppState } from '../store';
import { connect } from 'react-redux';
import { toggleDeviceUnlockModal } from '../store/modal'


const digits = [
  [7,8,9],
  [4,5,6],
  [1,2,3],
]

interface StateProps {
  open: boolean;
  device: Device | null;
}

interface DispatchProps {
  toggle: typeof toggleDeviceUnlockModal;
}

type Props = StateProps & DispatchProps

interface State {
  pin: string;
  submitting: boolean;
  error: string | null;
  pressed: number | null;
}

const initialState = {
  pin: '',
  submitting: false,
  error: null,
  pressed: null,
};

class EnterPinModal extends React.Component<Props, State> {
  state: State = initialState;

  async enterPin() {
    const { pin, submitting } = this.state;
    const { device } = this.props;
    if (!submitting) {
      try {
        this.setState({ submitting: true })
        await api.enterPin({ pin });
        this.toggle()
      } catch(error) {
        this.setState({ 
          error: error.message,
          pin: '',
          submitting: false,
         });
        // Prompt another pin so that user can try again  
        // Annoying that typescript makes me check this ...
        if (device) {
          setTimeout(
            () => api.promptPin({ path: device.path}),
            1000
          );
        }
      }
    }
  }

  handlePinClick(digit: number) {
    if (!this.state.submitting) {
      this.setState({ pin: this.state.pin + String(digit) });
    }
  }

  backspace() {
    if (!this.state.submitting) {
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
    this.props.toggle();
  }

  handleClosed() {
    api.deletePrompt();
  }

  componentWillUnmount() {
    this.handleClosed();
  }

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
    const { submitting } = this.state;
    return (
      <ModalFooter>
        {this.renderError()}
        <Button color="danger" onClick={this.backspace.bind(this)}>
          Backspace
        </Button>
        <Button color="secondary" onClick={this.enterPin.bind(this)}>
          {submitting ? <Spinner/> : "Submit"}
        </Button>
      </ModalFooter>
    )
  }

  render() {
		// TODO: accept an optional "device" prop and only display that device if present 
    const { open } = this.props;
    return (
			<Modal isOpen={open} toggle={this.toggle.bind(this)} className="PinModal" onClosed={this.handleClosed}>
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
    device: state.modal.deviceUnlock.device,
    open: state.modal.deviceUnlock.open,
  }
}

export default connect(
  mapStateToProps,
  { toggle: toggleDeviceUnlockModal },
)(EnterPinModal);
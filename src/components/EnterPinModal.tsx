import React from 'react';
import { Button, Modal, ModalHeader, ModalFooter, ModalBody, Row, Spinner } from 'reactstrap';
import api from '../api'
import { Device } from '../types';

const digits = [
  [7,8,9],
  [4,5,6],
  [1,2,3],
]

interface Props {
	toggle(): any;
  isOpen: boolean;
  device: Device | null;
}

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
}

export default class EnterPinModal extends React.Component<Props, State> {
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

  getStyles(digit: number) {
    let style = {
      height: '100px',
      width: '100px',
      backgroundColor: '#868e96',  // Bootstrap's "secondary" grey
      margin: '10px',
    }
    if (this.state.pressed === digit) {
      style['backgroundColor'] = '#ced4da'  // lighter grey
    }
    return style;
  }

  handleMouseDown(digit: number) {
    if (!this.state.submitting) {
      this.setState({ pressed: digit })
    }
  }

  handleMouseUp(digit: number) {
    if (!this.state.submitting) {
      this.setState(prevState => ({
        pin: prevState.pin + String(digit),
        pressed: null,
      }));
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
      <div>
        {digits.map((row: number[]) => {
          return <Row>{row.map((digit: number) => 
              <div style={this.getStyles(digit)}
                   onMouseDown={() => this.handleMouseDown(digit)}
                   onMouseUp={() => this.handleMouseUp(digit)}/>
            )}</Row>
        })}
        <div>PIN: {"•".repeat(pin.length)}</div>
      </div>
    )
  }

  toggle() {
    this.setState(initialState)
    api.deletePrompt().then(this.props.toggle)
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
    const { isOpen } = this.props;
    return (
			<Modal isOpen={isOpen} toggle={this.toggle.bind(this)}>
				<ModalHeader toggle={this.toggle.bind(this)}>EnterPin</ModalHeader>
				<ModalBody>
          {this.renderPin()}
				</ModalBody>
        {this.renderFooter()}
			</Modal>
		)
	}
}
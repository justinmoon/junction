import React from 'react';
import { Button, Modal, ModalHeader, ModalFooter, ModalBody } from 'reactstrap';

interface Props {
	toggle(): any;
	isOpen: boolean;
}

export default class AddSigners extends React.Component<Props> {
  render() {
		// TODO: accept an optional "device" prop and only display that device if present 
		const { toggle, isOpen } = this.props;
		return (
			<Modal isOpen={isOpen} toggle={toggle}>
				<ModalHeader toggle={toggle}>Device Instructions</ModalHeader>
				<ModalBody>
					<h3 className="text-center mb-3">Trezor</h3>
					<ul>
						<li>Plug in</li>
						<li>Trezor T: enter PIN on device</li>
						<li>Trezor One: close this modal and click the "Unlock" button in the "Add Signers" section, which will prompt you to enter your passphrase in Junction</li>
					</ul>
					<h3 className="text-center mb-3">ColdCard</h3>
					<ul>
						<li>Plug in and enter the PIN on the device</li>
						<li>Set coldcard to "testnet" mode in "Settings &gt; Blockchain &gt; Testnet: BTC"</li>
					</ul>
					<h3 className="text-center mb-3">Ledger</h3>
					<ul>
						<li>Enter PIN on the device and navigate to the testnet app on your Ledger</li>
						<li>If it's unlocked, in testnet app and doesn't show up -- unplug and try again.</li>
						<li>If you don't have the testnet app installed on your Ledger:</li>
						<ul>
							<li>Open "Ledger Live" desktop app (you can install "Ledger Live" <a href="https://support.ledger.com/hc/en-us/articles/360006395553-Download-and-install-Ledger-Live">here).</a></li>
							<li>Click the settings gear icon in top right.</li>
							<li>Click "Experimental features" tab at top.</li>
							<li>Enable "Developer mode".</li>
							<li>Click the "Manager" tab on left.</li>
							<li>Enter Ledger pin and accept the "Allow Ledger manager?" prompt on device screen.</li>
							<li>Search for and install the "Bitcoin Test" app.</li>
						</ul>
					</ul>
				</ModalBody>
				<ModalFooter>
					<Button color="secondary" onClick={toggle}>OK</Button>
				</ModalFooter>
			</Modal>
		)
	}
}
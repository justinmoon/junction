import React from 'react'
import { Modal, OverlayTrigger, Tooltip, ButtonToolbar, Table, Form, Button, Nav, Container, Col, Row } from 'react-bootstrap'

function DevicePopup(props) {
  return (
    <Modal
      {...props}
      size="lg"
      aria-labelledby="contained-modal-title-vcenter"
      centered
    >
      <Modal.Header closeButton>
        <Modal.Title id="contained-modal-title-vcenter">
          Trezor
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>
          Plug it in, you doofus
        </p>
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={props.onHide}>Close</Button>
      </Modal.Footer>
    </Modal>
  );
}

export default function WalletBanner() {
    const [modalShow, setModalShow] = React.useState(false);
    return (
      <div>
      <Row className="justify-content-center">
        <h1>trezor_ledger_coldcard</h1>
      </Row>
      <Row className="justify-content-center">
        <ButtonToolbar className="text-center">
          <OverlayTrigger
            key={1}
            placement="top"
            overlay={
              <Tooltip id={1}>
                <strong>Unlocked</strong>.
              </Tooltip>
            }
          >
            <Button size="sm" className="mx-2" variant="success" onClick={() => setModalShow(true)}>trezor</Button>
          </OverlayTrigger>
          <OverlayTrigger
            key={2}
            placement="top"
            overlay={
              <Tooltip id={2}>
                <strong>Visible, Locked</strong>.
              </Tooltip>
            }
          >
            <Button size="sm" className="mx-2" variant="warning">ledger</Button>
          </OverlayTrigger>
          <DevicePopup
            show={modalShow}
            onHide={() => setModalShow(false)}
          />
          <OverlayTrigger
            key={3}
            placement="top"
            overlay={
              <Tooltip id={3}>
                <strong>Not Visible</strong>.
              </Tooltip>
            }
          >
            <Button size="sm" className="mx-2" variant="danger">ledger</Button>
          </OverlayTrigger>
        </ButtonToolbar>
      </Row>
      </div>
    )
}

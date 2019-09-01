import React from 'react'
import { Form, Button, Nav, Container, Col, Row } from 'react-bootstrap'

export default class Settings extends React.Component {
  constructor(props) {
    super(props)
    this.state = {}
    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }

  handleSubmit(event) {
    event.preventDefault()
    console.log(this.state)
  }

  handleChange(key, event) {
    console.log(key, event);
    this.setState({ [key]: event.target.value })
  }

  render() {
    return (
      <div>
        <h2 className="text-center mb-4">RPC Settings</h2>
        <h6 className="text-center mb-4">Configure Testnet RPC Parameters. Mainnet coming soon ™️.</h6>
        <Form onSubmit={this.handleSubmit}>

          <Form.Group as={Row} controlId="rpcUsername">
            <Form.Label column xs={4}>RPC Username</Form.Label>
            <Col xs={8}>
              <Form.Control type="text" onChange={e => this.handleChange('rpcUsername', e)}/>
            </Col>
          </Form.Group>
          <Form.Group as={Row} controlId="rpcPassword">
            <Form.Label column xs={4}>RPC Password</Form.Label>
            <Col xs={8}>
              <Form.Control type="text" onChange={e => this.handleChange('rpcPassword', e)}/>
            </Col>
          </Form.Group>
          <Form.Group as={Row} controlId="rpcHost">
            <Form.Label column xs={4}>RPC Host</Form.Label>
            <Col xs={8}>
              <Form.Control type="text" onChange={e => this.handleChange('rpcHost', e)}/>
            </Col>
          </Form.Group>
          <Form.Group as={Row} controlId="rpcPort">
            <Form.Label column xs={4}>RPC Port</Form.Label>
            <Col xs={8}>
              <Form.Control type="text" onChange={e => this.handleChange('rpcPort', e)}/>
            </Col>
          </Form.Group>
          <div className="d-flex">
            <Button variant="primary" type="submit" className="ml-auto">
              Submit
            </Button>
          </div>
        </Form>
      </div>
    )
  }
}

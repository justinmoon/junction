import React from 'react';
import { Navbar, NavbarBrand, Container, Col } from 'reactstrap';
import Enumerate from './components/Enumerate'

const App: React.FC = () => {
  return (
    <div>
      <Navbar color="light">
        <NavbarBrand>Junction</NavbarBrand>
      </Navbar>
      <Container>
        <Col>
          <Enumerate/>
        </Col>
      </Container>
    </div>
  );
}

export default App;

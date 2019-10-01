import React from 'react';
import { Container, Row, Col, Button } from 'reactstrap';
import './ErrorScreen.css';

interface Props {
  error: Error;
  errorInfo?: React.ErrorInfo | null;
}

export default class ErrorScreen extends React.PureComponent<Props> {
  private reload() {
    window.location.reload();
  }

  render() {
    const { error, errorInfo } = this.props;
    const errorString = error.stack || error.toString();

    // TODO: Fill out Junction version number, system specs etc?
    let errorBody = 'I encountered the following uncaught error:\r\n```\r\n' + errorString + '\r\n```';
    if (errorInfo) {
      errorBody += '\r\n```\r\nThe above error occured in the following component stack:' + errorInfo.componentStack + '\r\n```';
    }

    let errorTitle = `Got a ${error.name} error`
    if (errorInfo) {
      const components = errorInfo.componentStack.match(/in ([a-zA-Z]*)/)
      const componentName = components ? components[1] : 'an unknown';
      errorTitle += ` in ${componentName} component`;
    }

    const ghIssueUrl = encodeURI(`https://github.com/justinmoon/junction/issues/new?title=${errorTitle}&body=${errorBody}`);
    return (
      <div className="ErrorScreen">
        <Container>
          <Row>
            <Col size={12}>
              <div className="ErrorScreen-content">
                <h1>Uh oh, something went wrong</h1>
                <p>
                  The app experienced an unexpected error. Please report it using
                  the link below, then restart the app. We'll try to get it fixed
                  as soon as possible.
                </p>
                <pre>{errorString}</pre>
                <div className="ErrorScreen-content-actions">
                  <Button outline color="danger" size="lg" onClick={this.reload}>
                    Restart Junction
                  </Button>
                  <Button
                    tag="a"
                    color="danger"
                    size="lg"
                    target="_blank"
                    rel="noopener nofollow"
                    href={ghIssueUrl}
                  >
                    Report Issue
                  </Button>
                </div>
              </div>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }
}


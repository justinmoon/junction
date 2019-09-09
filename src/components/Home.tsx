import React from 'react';
import Enumerate from './Enumerate'

export default class Home extends React.Component {
  render() {
    return (
      <div>
        <h1>Welcome home!</h1>
        <p>Here are your devices:</p>    
        <Enumerate />
      </div>
    )
  }
}

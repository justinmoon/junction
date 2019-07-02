import React from 'react';
import './App.css';
import QRCode from 'qrcode.react';
import axios from 'axios';

class App extends React.Component{
  constructor(props){
    super(props);
    this.state = {
      qrtext:"Nothing interesting here",
      txlist:[],
    };
    this.refresh();
  }
  handleClick(e){
    console.log(e.address);
    this.setState({qrtext: "bitcoin:"+e.address+"?amount="+e.amount});
  }
  refresh(){
    axios.get('http://localhost:5000/')
    .then((response) => {
      this.setState(Object.assign({}, this.state, {txlist: response.data}));
      console.log(response.data)
    });
  }
  render(){
    console.log("render");
    return (
      <div className="App">
        <header className="App-header">
          <QRCode value={this.state.qrtext} includeMargin={true} size={300}/>
          <div>{this.state.qrtext}</div>
          <div onClick={() => this.refresh()}>Click to refresh</div>
          <br/>
          <table><tbody>
          {
            this.state.txlist.map((v, i)=>{
              return (
                <tr key={i} onClick={() => this.handleClick(v)}>
                  <td>{v.address}</td>
                  <td>{v.amount} BTC</td>
                </tr>)
            })
          }
          </tbody></table>
        </header>
      </div>
    );
  }
}

export default App;

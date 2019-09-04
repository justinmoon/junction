import React from 'react'
import { enumerate } from '../api'

// class Enumerate extends React.Component {
//   constructor(props) {
//     super(props);
//     this.state = {
//       error: null,
//       isLoaded: false,
//       devices: []
//     };
//   }

//   componentDidMount() {
//     enumerate().then(
//       (result) => {
//         this.setState({
//           isLoaded: true,
//           devices: result
//         });
//       },
//       (error) => {
//         this.setState({
//           isLoaded: true,
//           error
//         });
//       }
//     )
//   }
//   render() {
//     const { error, isLoaded, devices } = this.state
//     if (error) {
//       return <div>Error: {error.message}</div>;
//     } else if (!isLoaded) {
//       return <div>Loading...</div>;
//     } else {
//       return (
//         <ul>
//           {devices.map(devices => (
//             <li key={device.name}>
//               {device.type} {device.fingerprint}
//             </li>
//           ))}
//         </ul>
//       );
//     }
//   }
// }

const Enumerate: React.FC = () => {
  return (
    <div>
      hello, world
    </div>
  );
}

export default Enumerate

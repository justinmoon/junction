import React from 'react';
import { Signer } from '../types'

interface Props {
  signers: Signer[];
}

class Signers extends React.Component<Props> {
  render() {
    const { signers } = this.props;
    // FIXME: this table is whack
    return (
      <table>
        <thead>
          <tr>
            <th scope="col">Device</th>
            <th scope="col" className="text-right">Action</th>
          </tr>
        </thead>
        <tbody>
        {signers.map((signer: Signer, index: number) => 
          <tr key={signer.fingerprint}>
            <td>{ signer.name }</td>
            <td>Signer #{index}</td>
          </tr>
        )}
        </tbody>
      </table>
    )
  }
}

export default Signers;
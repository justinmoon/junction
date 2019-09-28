import React from 'react';
import { Signer } from '../types'
import { MyTable } from './Toolbox'

interface Props {
  signers: Signer[];
}

class Signers extends React.Component<Props> {
  render() {
    const { signers } = this.props;
    // FIXME: this table is whack
    return (
      <MyTable>
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col" className="text-right">Device</th>
          </tr>
        </thead>
        <tbody>
        {signers.map((signer: Signer) => 
          <tr key={signer.fingerprint}>
            <td>{ signer.name }</td>
            <td className="text-right">{ signer.type }</td>
          </tr>
        )}
        </tbody>
      </MyTable>
    )
  }
}

export default Signers;
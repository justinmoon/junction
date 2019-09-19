import React, { FunctionComponent } from 'react';
import { Card, Table } from 'reactstrap';

let containerStyle = {
  'margin': '0 auto',
  // FIXME
  // 'max-width': '400px',
}

export const MyCard: FunctionComponent = props => (
  <div style={containerStyle}>
    <Card className='p-3'>
      {props.children}
    </Card>
  </div>
)


export const MyTable: FunctionComponent = props => (
  <MyCard>
    <Table borderless>
      {props.children}
    </Table>
  </MyCard>
)

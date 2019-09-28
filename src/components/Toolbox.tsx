import React, { FunctionComponent } from 'react';
import { Card, Table, Button, Spinner } from 'reactstrap';
import classnames from "classnames";

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

// FIXME: typing
// interface LoadingButtonProps {
//   children: any;
//   loading: any;
//   block: any;
// }

export class LoadingButton extends React.Component<any> {
  render() {
    const { children, loading, block, ...rest } = this.props
    return (
      <Button {...rest} block={block}>
        {!(block && !loading) && (
          <Spinner
            className={classnames({
              "position-relative": true,
              "button-style": !block,
              visible: loading,
              invisible: !loading
            })}
            size="sm"
            // type="grow"
          />
        )}
        {!(block && loading) && (
          <span
            className={classnames({
              invisible: loading,
              visible: !loading,
              "span-style": !block
            })}
          >
            {children}
          </span>
        )}
      </Button>
    )
  }
}
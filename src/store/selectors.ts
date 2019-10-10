export const notNull = (val: any) => {
  if (val === null) {
    throw Error('Cannot be null')
  }
  return val
}
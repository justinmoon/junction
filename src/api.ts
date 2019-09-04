export function enumerate () {
  return fetch('http://localhost:5000/enumerate')
    .then(res => res.json())
}

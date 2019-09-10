export function enumerate () {
  return fetch('http://localhost:5000/enumerate')
    .then(res => res.json())
    .then(res => {
      if (res.error) {
        throw new Error(res.error);
      } else if (Array.isArray(res) && res[0].error) {
        throw new Error(res[0].error);
      } else {
        return res;
      }
    });
}

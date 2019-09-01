# To run:

In addition to python instructions in README

```
npm install
npm start
```

## Development

`python dev.py` to run dev backend server
`npm start` in `frontend/` to run hot-reloading react server
`npm start` in base directory to run in electron

## Notes

- Had to do [https://github.com/hundredrabbits/Orca/issues/91#issuecomment-508750882](this hack) to get electron to run on arch ...
- I wrote a "dev" command in frontend/package.json that isn't being used currently. Remove this if it's never used ...

## React Router
- [nested routing](https://reacttraining.com/react-router/web/guides/quick-start/example-nested-routing) would be a good way to do routing with multiple wallets.
- [this](https://reacttraining.com/react-router/web/example/custom-link) will highlight active route in navbar
- [minimal sidebar](https://reacttraining.com/react-router/web/example/sidebar)
- [react-transition-group](https://codesandbox.io/s/3vo2mnwl9p?from-embed) can do transitions
- [nested routes](// then our route config

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

## Dependencies

- "react-router-bootstrap" made bootstrap "<Link/>" behave correctly w/ react-router
- I wrote a "dev" command in frontend/package.json that isn't being used currently. Remove this if it's never used ...
  - "watch"

## React Router
- [nested routing](https://reacttraining.com/react-router/web/guides/quick-start/example-nested-routing) would be a good way to do routing with multiple wallets.
- [this](https://reacttraining.com/react-router/web/example/custom-link) will highlight active route in navbar
- [minimal sidebar](https://reacttraining.com/react-router/web/example/sidebar)
- [react-transition-group](https://codesandbox.io/s/3vo2mnwl9p?from-embed) can do transitions
- [nested routes](// then our route config

## Packaging

I got [this project](https://github.com/electron-userland/electron-webpack-quick-start) to runa[(here)](/home/justin/dev/projects/electron-package-demo/new-electron-webpack-project/electron-webpack-quick-start)

I'm copying the dev dependencies to get this working here -- but note that it uses electron 5 instead of electron 6 (newest version).

### codementor tutorial

/home/justin/dev/github/electron-cra-boilerplate

[this](https://www.codementor.io/randyfindley/how-to-build-an-electron-app-using-create-react-app-and-electron-builder-ss1k0sfer#comment-wznez4xhb)
- changed package.json to `"electron-pack": "build -l"`
  - to get a multi-platform build it should be `build -mwl` [(docs)](https://www.electron.build/multi-platform-build)
- [how to build windows on linux](https://www.electron.build/multi-platform-build#docker)
  - run `yarn build -w` inside the container to just build for windows

- ^^ not that comment 

### PyInstaller

I was able to get an executable with `pyinstaller electron.py` ... output as `build/electron/electron`

[This tutorial](https://ourcodeworld.com/articles/read/154/how-to-execute-an-exe-file-system-application-using-electron-framework) shows how to run an executable file from electron (pyinstaller output)

## Bait & Switch

- don't forget python-shell dep
- don't touch any python stuff. that stuff doesn't need to move yet ...# To run:

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

## Dependencies

- "react-router-bootstrap" made bootstrap "<Link/>" behave correctly w/ react-router
- I wrote a "dev" command in frontend/package.json that isn't being used currently. Remove this if it's never used ...
  - "watch"

## React Router
- [nested routing](https://reacttraining.com/react-router/web/guides/quick-start/example-nested-routing) would be a good way to do routing with multiple wallets.
- [this](https://reacttraining.com/react-router/web/example/custom-link) will highlight active route in navbar
- [minimal sidebar](https://reacttraining.com/react-router/web/example/sidebar)
- [react-transition-group](https://codesandbox.io/s/3vo2mnwl9p?from-embed) can do transitions
- [nested routes](// then our route config

## Packaging

I got [this project](https://github.com/electron-userland/electron-webpack-quick-start) to runa[(here)](/home/justin/dev/projects/electron-package-demo/new-electron-webpack-project/electron-webpack-quick-start)

I'm copying the dev dependencies to get this working here -- but note that it uses electron 5 instead of electron 6 (newest version).

### codementor tutorial

/home/justin/dev/github/electron-cra-boilerplate

[this](https://www.codementor.io/randyfindley/how-to-build-an-electron-app-using-create-react-app-and-electron-builder-ss1k0sfer#comment-wznez4xhb)
- changed package.json to `"electron-pack": "build -l"`
  - to get a multi-platform build it should be `build -mwl` [(docs)](https://www.electron.build/multi-platform-build)
- [how to build windows on linux](https://www.electron.build/multi-platform-build#docker)
  - run `yarn && yarn build -w` inside the container to just build for windows

- ^^ not that comment 

### PyInstaller

I was able to get an executable with `pyinstaller electron.py` ... output as `build/electron/electron`

[This tutorial](https://ourcodeworld.com/articles/read/154/how-to-execute-an-exe-file-system-application-using-electron-framework) shows how to run an executable file from electron (pyinstaller output)

## Bait and switch

- don't forget [python-shell dep](https://github.com/electron-userland/electron-builder/issues/2529)
- don't touch the python
- yarn installations gets a lot of "too old" warnings
- `yaarn start` doesn't work in the original project. seems it's trying to import "crypto" project in the browser -- but it's a node thing, not a browser thing.
- I had to [manually add](https://github.com/electron-userland/electron-builder/issues/2529) `jquery` and `popper.js`

## Windows build

Had to build a custom docker container b/c node version was too old in `electronuserland/builder:wine` ... not sure why this is ...

```
docker build -t junction .
```

there are some permissions problems in the output `dist/` folder ... some stuff owned by root ...


## FUCK ME

- everything gets copied into dist/electron_prod -- hwi, frontend.py, build directory
    - but this isn't getting found when running in electron

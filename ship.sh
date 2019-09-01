# FIXME: should use electron.py, not dev.py
pyinstaller -y electron.py --add-data "build:build"
pyinstaller -y electron.spec
yarn electron-dev

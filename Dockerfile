from cdrx/pyinstaller-linux:python3

RUN apt-get install -y --no-install-recommends libusb-1.0-0-dev libudev-dev python3-pyqt5 python3-pyqt5.qtwebengine python3-pyqt5.qtwebchannel libqt5webkit5-dev

ENTRYPOINT ["/entrypoint.sh"]


Clone HWI into contrib/ (FIXME, this is stupid)

To build a linux binary:

```
docker run -v "$(pwd):/src/" cdrx/pyinstaller-linux"
```

Note: this docker image is built from ubuntu version 12, so it will probably have an ancient glibc version -- a good thing because if built with new glibc versions sometimes older computers won't be able to run.

## Running desktop.py locally

symlink `build` to `server/build` (FIXME)

## Windows

- trying to build in windows
- docker doesn't owkr
- trying with a fresh build.
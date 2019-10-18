import sys
from threading import Thread
from time import sleep

import webview

from server import serve_windows, serve_unix

def url_ok(url, port):
    # Use httplib on Python 2
    try:
        from http.client import HTTPConnection
    except ImportError:
        from httplib import HTTPConnection

    try:
        conn = HTTPConnection(url, port)
        conn.request('GET', '/')
        r = conn.getresponse()
        return r.status == 200
    except:
        print('Server not started')
        return False

HOST = '127.0.0.1'
PORT = 37128

if sys.platform == 'win32':
    print('RUNNING WINDOWS')
    target = serve_windows
else:
    target = serve_unix

server = Thread(target=target)
server.daemon = True
server.start()

print('starting server')

while not url_ok(HOST, PORT):
    sleep(.1)

print('server started')

webview.create_window(
    'Junction',
    f'http://{HOST}:{PORT}',
    # min_size=(600, 400),
    # text_select=True,
)
# webview.start(debug=True)

# if sys.platform == 'win32':
#     print('starting cef')
#     webview.start(http_server=True, gui='cef')
# else:
#     webview.start(http_server=True, gui='qt')
webview.start(http_server=True)

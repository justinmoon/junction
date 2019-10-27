from multiprocessing import Process
from time import sleep

import webview

from server import serve

from http.client import HTTPConnection

# Constants
HOST = 'localhost'
PORT = 37128
URL  = f'http://{HOST}:{PORT}'
# Server
server = Process(target=serve)
# Frontend
webview.create_window(
    'Junction',
    f'http://{HOST}:{PORT}',
    min_size=(600, 400),
    text_select=True,
)

def server_running():
    '''Helper to see if server is running'''
    try:
        conn = HTTPConnection(HOST, PORT)
        conn.request('GET', '/')
        r = conn.getresponse()
        return r.status == 200
    except:
        print('Server not started')
        return False

if __name__ == '__main__':
    # Run server process
    server.start()
    # Wait for server to start
    print('Starting server')
    while not server_running():
        sleep(1)
    print('Server started')
    # Run frontend
    webview.start(http_server=True)

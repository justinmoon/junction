from threading import Thread

import webview

from server import server

server = Thread(
    target=server.run, 
    kwargs={
        'host': '0.0.0.0',
        'port': 37128,
        'threaded': False,
    },
)
server.start()

webview.create_window('Hello world', 'http://localhost:37128')
webview.start(debug=True)


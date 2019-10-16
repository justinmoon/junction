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

webview.create_window(
    'Junction',
    'http://localhost:37128',
    min_size=(600, 400),
    text_select=True,
)
webview.start(debug=True)


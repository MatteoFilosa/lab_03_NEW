# file: gevent_app.py
from gevent.pywsgi import WSGIServer
from server import app


http_server = WSGIServer(('127.0.0.1', 5000), app)
http_server.serve_forever()

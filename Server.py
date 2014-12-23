import tornado.web
import tornado.ioloop

import WebSocketServer


class Server:

    def __init__(self):
        self.server_application = tornado.web.Application()

    def start(self, _path, _port):
        self.server_application = tornado.web.Application([(r"/" + _path, WebSocketServer.WebSocketServer)])
        self.server_application.listen(_port)
        print("Server Ready!")
        tornado.ioloop.IOLoop.instance().start()
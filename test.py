import tornado.ioloop
import tornado.web
import tornado.websocket
import time

import DbConnector


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    db_connection = DbConnector.DbConnector()

    def open(self):
        print "WebSocket opened"
        self.write_message(u"HELLO CLIENT")
        self.write_message(u"How are you?")
        self.write_message(u"Client?")
        self.write_message(u"Reply to me, honey?")
        self.write_message(u"I even brought cake?")
        self.write_message(u"CLIEEEEEEEEEEEEEEEEEEENT?")
        self.write_message(u"Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... Client... ")

    def on_message(self, message):
        print(message)
        sql_statement = 'INSERT INTO log (sender,timestamp,message_type,message) VALUES(%s,%s,%s,%s)'
        sql_args = ('127.0.0.1', int(time.time()), 'websocket_message', message)
        self.db_connection.insert(sql_statement, sql_args)
        self.write_message(u"You said: " + message)

    def on_close(self):
        print "WebSocket closed"


application = tornado.web.Application([
    (r"/websocket", EchoWebSocket),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()



import tornado.websocket
import json
import uuid
import time

import Wikigame
import ControlServer


class WebSocketServer(tornado.websocket.WebSocketHandler):
    uuid = None
    game_list = dict()
    control_server = ControlServer.ControlServer()

    def check_origin(self, origin):
        return True

    def write_json_message(self, _type, _message):
        message_data = {"type": _type,"timestamp": int(time.time()), "message": _message}
        message_string = json.dumps(message_data)
        print(">> " + message_string)
        self.write_message(message_string)

    def handle_message(self, _message_package):
#        print("FORWARDING TO: " + self.uuid)

        if type(_message_package) != type(dict()):
            print("INVALID INCOMING MESSAGE")
            return
        self.control_server.broadcast(str(_message_package['type']) + " -> " + str(_message_package['message']))
        self.game_list[self.uuid].handle_message(_message_package)

    def open(self):
        print "###WebSocket opened"
        self.uuid = str(uuid.uuid4())
        self.game_list[self.uuid] = Wikigame.WikiGame(self, self.uuid)
        self.control_server.broadcast("Opened connection")

    def on_message(self, _message):
        print("<< " + _message)
        message_package = json.loads(_message)
        self.handle_message(message_package)

    def on_close(self):
        print "###WebSocket closed"






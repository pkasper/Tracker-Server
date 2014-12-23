import socket
import sys
import time

from thread import *


class ControlServer:
    connections = list()
    port = 31337
    control_socket = None

    def __init__(self):
        start_new_thread(self.start_server, ())

    def start_server(self):
        print("Initializing Control Server")
        self.control_socket = socket.socket()

        try:
            self.control_socket.bind(('', self.port))
        except socket.error as socket_error:
            print(socket_error[1])
            return

        self.control_socket.listen(10)
        print("Control Server Listening")

        while True:
            connection, address = self.control_socket.accept()
            print 'Connected with ' + address[0] + ':' + str(address[1])
            start_new_thread(self.handle_connection, (connection,))

        self.control_socket.close()

    def handle_connection(self, _connection):
        self.connections.append(_connection)
        while True:
            incoming_data = _connection.recv(512)
            print(">> CTRL >> " + incoming_data)

    def broadcast(self, _message):
        for connection in self.connections:
            connection.send(_message)
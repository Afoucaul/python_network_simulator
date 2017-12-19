#!/usr/bin/python3


"""server.py

Usage:
    server.py <port>
"""

import docopt
import select
import socket as net

if __name__ == '__main__':
    import messages
    from settings import SIZE_LENGTH
else:
    from . import messages
    from .settings import SIZE_LENGTH


class Server:
    def __init__(self, port):
        self.socket = net.socket(net.AF_INET, net.SOCK_STREAM)
        self.port = port
        self.slaves = {}
        self.rev_slaves = {}

    def run(self):
        self.socket.bind(("localhost", self.port))
        self.port = self.socket.getsockname()[1]
        print("Server started on port {}.".format(self.port))
        print("Now listening for connections.")
        self.socket.listen()
        while True:
            toWait = [self.socket] + list(self.slaves.values())
            result = select.select(toWait, [], [])[0]

            if self.socket in result:
                result.remove(self.socket)
                conn, addr = self.socket.accept()
                msg = self.receive_message(conn)
                self.on_accept(conn, msg.port)
                print("Accepted a connection from port {}, running its node "
                      "on port {}".format(addr[1], msg.port))
                print("Current working nodes: {}".format(
                      list(self.slaves.keys())))

            for conn in result:
                print("Socket associated to port {} is ready".format(
                    self.rev_slaves[conn]))
                message = self.receive_message(conn)
                print(message)

    def send_message(self, port, msg):
        if isinstance(msg, messages.Message):
            msg = bytes(msg)
        if not isinstance(msg, bytes):
            raise ValueError("A bytes object is required")

        size = bytes("{0:0>{1}}".format(len(msg), SIZE_LENGTH), 'ascii')
        dest = self.slaves[port]
        dest.send(size)
        dest.send(msg)

    def receive_message(self, connection):
        buffer = b""
        try:
            size = int(connection.recv(SIZE_LENGTH))
            while len(buffer) < size:
                buffer += connection.recv(4096)
            return messages.make(buffer)

        except ValueError:
            print("Invalid message")
            self.close_connection(connection)

    def on_accept(self, connection, newPort):
        self.slaves[newPort] = connection
        self.rev_slaves[connection] = newPort

        slaves = list(self.slaves.keys())
        slaves.remove(newPort)
        self.send_message(newPort, messages.NodeListMessage(slaves))

        msg = messages.NewSlaveMessage(newPort)

        for port in self.slaves:
            if port != newPort:
                self.send_message(port, msg)

    def close_connection(self, connection):
        connection.close()
        port = self.rev_slaves[connection]
        self.rev_slaves.pop(connection)
        self.slaves.pop(port)
        print("Node {} left".format(port))

        msg = messages.SlaveLeftMessage(port)
        for port in self.slaves:
            self.send_message(port, msg)

    def start_simulation(self):
        msg = messages.StartSimulationMessage()

        for port in self.slaves:
            self.send_message(port, msg)


def start_server(port=0):
    server = Server(port)
    server.run()


def format_args(args):
    args['<port>'] = int(args['<port>'])


def main(args):
    format_args(args)
    port = args['<port>']

    server = Server(port)
    server.run()


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)

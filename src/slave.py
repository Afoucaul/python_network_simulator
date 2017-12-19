#!/usr/bin/python3


"""slave.py

Usage:
    slave.py <serverPort> [<port>]
"""


import docopt
import socket as net
import threading

if __name__ == '__main__':
    import messages
    from settings import SIZE_LENGTH
else:
    from . import messages
    from .settings import SIZE_LENGTH


def subscribable(method):
    def calling_method(instance, *args, **kwargs):
        method(instance, *args, **kwargs)
        for callback in calling_method.callbacks:
            # print(callback, args, kwargs)
            callback(*args, **kwargs)
    setattr(calling_method, "callbacks", [])

    return calling_method


class Slave(threading.Thread):
    def __init__(self, serverPort, port=0):
        super().__init__()

        self.serverSocket = net.socket(net.AF_INET, net.SOCK_STREAM)
        self.nodeSocket = net.socket(net.AF_INET, net.SOCK_DGRAM)
        self.serverPort = serverPort
        self.port = port
        self.neighbors = []

    def run(self):
        self.serverSocket.connect(("localhost", self.serverPort))
        self.nodeSocket.bind(("localhost", self.port))
        self.port = self.nodeSocket.getsockname()[1]
        print("Node running on port {}".format(self.port))
        msg = messages.NewSlaveMessage(self.port)
        self.send_message_to_server(msg)
        print("Connected to server")

        while True:
            msg = self.receive_message_from_server()

            if isinstance(msg, messages.NewSlaveMessage):
                self.on_new_slave(msg)

            elif isinstance(msg, messages.NodeListMessage):
                self.on_node_list(msg)

            elif isinstance(msg, messages.SlaveLeftMessage):
                self.on_slave_left(msg)

    def send_message_to_server(self, msg):
        if isinstance(msg, messages.Message):
            msg = bytes(msg)
        if not isinstance(msg, bytes):
            raise ValueError("A bytes object is required")

        size = bytes("{0:0>{1}}".format(len(msg), SIZE_LENGTH), 'ascii')
        self.serverSocket.send(size)
        self.serverSocket.send(msg)

    def receive_message_from_server(self):
        buffer = b""
        size = int(self.serverSocket.recv(SIZE_LENGTH))
        while len(buffer) < size:
            buffer += self.serverSocket.recv(4096)

        return messages.make(buffer)

    @subscribable
    def on_new_slave(self, msg):
        self.neighbors.append(msg.port)
        # print("A new node joined, listening on port {}".format(msg.port))

    @subscribable
    def on_node_list(self, msg):
        self.neighbors = msg.ports
        # print("Currently working neighbors: {}".format(self.neighbors))

    @subscribable
    def on_slave_left(self, msg):
        try:
            self.neighbors.remove(msg.port)
        except ValueError:
            print("Received SlaveLeftMessage with unknown port {}".format(
                msg.port))
        else:
            # print("Node {} left".format(msg.port))
            pass


def format_args(args):
    args['<serverPort>'] = int(args['<serverPort>'])
    if args['<port>'] is not None:
        args['<port>'] = int(args['<port>'])
    else:
        args['<port>'] = 0


def main(args):
    format_args(args)
    serverPort = args['<serverPort>']
    port = args['<port>']

    slave = Slave(serverPort, port)
    slave.run()


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)

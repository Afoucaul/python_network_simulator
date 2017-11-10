from .slave import Slave


class VirtualNode:
    def __init__(self, serverPort, port=0):
        self.slave = Slave(serverPort, port=port)
        self.slave.on_new_slave.callbacks.append(self.on_new_slave)
        self.slave.on_slave_left.callbacks.append(self.on_slave_left)

    @property
    def neighbors(self):
        return self.slave.neighbors

    @property
    def socket(self):
        return self.slave.nodeSocket

    @property
    def port(self):
        return self.slave.port

    def sendto(self, message, port):
        self.socket.sendto(message, ("localhost", port))

    def recvfrom(self):
        data, addr = self.socket.recvfrom(4096)
        return data, addr[1]

    def broadcast(self, message):
        for port in self.neighbors:
            self.sendto(message, port)

    def start(self):
        self.slave.start()

    def run(self):
        while True:
            pass

    def on_new_slave(self, msg):
        print("VirtualNode - slave joined: {}".format(msg.port))

    def on_slave_left(self, msg):
        print("VirtualNode - slave left: {}".format(msg.port))

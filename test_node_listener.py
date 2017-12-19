import sys
from src import VirtualNode


class SpeakerNode(VirtualNode):
    def run(self):
        while True:
            data, port = self.recvfrom()
            print("Received message {} from port {}".format(data, port))


if __name__ == '__main__':
    node = SpeakerNode(int(sys.argv[1]))
    node.start()
    node.run()

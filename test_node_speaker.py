import sys
import time
from src import VirtualNode


class SpeakerNode(VirtualNode):
    def run(self):
        while True:
            for n in self.neighbors:
                self.sendto(b"hello", n)
            time.sleep(1)


if __name__ == '__main__':
    node = SpeakerNode(int(sys.argv[1]))
    node.start()
    node.run()

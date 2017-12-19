from importlib import import_module


# Submodule imports

messages = import_module("{}.messages".format(__name__))
server = import_module("{}.server".format(__name__))
slave = import_module("{}.slave".format(__name__))
virtual_node = import_module("{}.virtual_node".format(__name__))


# Name imports

Slave = slave.Slave

Server = server.Server
start_server = server.start_server

VirtualNode = virtual_node.VirtualNode

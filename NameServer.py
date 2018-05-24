#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function
from NameService import *
import types

try:
    import SimpleXMLRPCServer as xmlrpc_server
except:
    import xmlrpc.server as xmlrpc_server

def setupXmlrpc(funcs, port=8080, global_var=globals()):
    server = xmlrpc_server.SimpleXMLRPCServer(('localhost', port))
    for x in funcs :
        if type(x) == str and global_var.has_key(x) :
            server.register_function(global_var[x])
        elif type(x) == types.FunctionType:
            server.register_function(x)
    server.register_introspection_functions()
    return server


def main():
    ns = NameService()
    ns.run()

if __name__ == '__main__':
    main()

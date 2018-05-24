#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function
from NameService import *
import types
import signal
import time

try:
    import SimpleXMLRPCServer as xmlrpc_server
except:
    import xmlrpc.server as xmlrpc_server

server = None
name_server = None
shutdown_flag = False

def sig_int_handle(signum, frame):
    stop_server()

def stop_server():
    global shutdown_flag
    print("Call shutdown")
    shutdown_flag=True
    return 'OK'

def start_server():
    global server, shutdown_flag
    if server is None:
        setupXmlrpc()
    shutdown_flag = False
    server.timeout = 1
    while not shutdown_flag:
        try:
            server.handle_request()
        except:
            time.sleep(0.01)
            pass

def getFunctions():
    global_var = globals()
    res = []
    for x in global_var.keys():
       if type(global_var[x]) == types.FunctionType:
           res.append(x)
    return res

def add(x, y):
    return x+y

def registerFunction(name):
    global server
    global_var = globals()
    try:
        if type(global_var[name]) == types.FunctionType:
            server.register_function(global_var[name])
            return "Registered"
        else:
            return name+" is not function."
    except:
            return "Fail to register_function: "+name
    return False

def setupXmlrpc(funcs=[], port=8080, global_var=globals()):
    global server
    server = xmlrpc_server.SimpleXMLRPCServer(('localhost', port))
    server.register_function(stop_server)
    server.register_function(initNS)
    server.register_function(getFunctions)
    server.register_function(registerFunction)
    for x in funcs :
        if type(x) == str and global_var.has_key(x) :
            if type(global_var[x]) == types.FunctionType:
                server.register_function(global_var[x])
            else:
                print(x, "is not function")
        elif type(x) == types.FunctionType:
            server.register_function(x)
    server.register_introspection_functions()
    return server

def initNS():
    global name_server
    if name_server is None:
        name_server = NameService()
        return "OK"
    return "Already running..."

def main():
    global name_server
    name_server = NameService()
    name_server.run()

if __name__ == '__main__':
    main()
else:
    signal.signal(signal.SIGINT, sig_int_handle)
    setupXmlrpc()

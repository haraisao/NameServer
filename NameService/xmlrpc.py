#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function
from main import *
import types
import signal
import time

import traceback

import OpenRTM_aist, RTC, OpenRTM, SDOPackage, RTM
import CosNaming

try:
    import SimpleXMLRPCServer as xmlrpc_server
except:
    import xmlrpc.server as xmlrpc_server


server = None
name_server = None
shutdown_flag = False

def NameServer():
    global name_server
    return name_server

def sig_int_handle(signum, frame):
    _stop()

from rtm import *
##############################
#  Xmlrpc
#
def _stop():
    global shutdown_flag
    print("Call shutdown")
    shutdown_flag=True
    return 'OK'
#
#
def _start():
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
#
#
def getFunctions():
    global_var = globals()
    res = []
    for x in global_var.keys():
       if type(global_var[x]) == types.FunctionType:
           res.append(x)
    return res
#
#
def getGlobals():
    global_var = globals()
    return global_var.keys()
#
#
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
#
#
def remoteExec(src):
    try:
      print (src)
      exec(src,globals())
    except:
      import traceback
      traceback.print_exc()
      return False
    return True

#
#
def remoteEval(src):
    try:
      print (src)
      print(eval(src,globals()))
    except:
      traceback.print_exc()
      return False
    return True


##############################################
#    
def _setup(funcs=[], port=8080, global_var=globals()):
    global server

    signal.signal(signal.SIGINT, sig_int_handle)
    server = xmlrpc_server.SimpleXMLRPCServer(('localhost', port))
    funcs = [ _stop, initNS, getFunctions, getGlobals,
              registerFunction,remoteExec,list,activate_rtc,
              deactivate_rtc,reset_rtc,exit_rtc,get_rtc_ports,
              get_connection_id, connect, disconnect]
    for x in funcs:
        server.register_function(x)

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
#
#
def initNS():
    global name_server
    if name_server is None:
        name_server = NameService()
        return "OK"
    return "Already running..."

if __name__ == '__main__':
    setup()

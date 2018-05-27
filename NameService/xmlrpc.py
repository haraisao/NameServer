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

import numpy

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


def sig_int_handle(signum, frame):
    _stop()

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

##############################
#  Name Service
#
def resolve_rtc(path):
    global name_server
    try:
      if name_server:
        obj = name_server.root_context.resolve_str(path)
      return  obj
    except:
      pass
    return None 
#
#
def get_rtc_ec(path):
    try:
      rtc = resolve_rtc(path)
      if rtc :
        return rtc, rtc.get_owned_contexts()
    except:
      pass
    return None
#
#
def activate_rtc(path):
    try:
      rtc, ecs = get_ec(path)
      if ecs[0] :
        return ecs[0].activate_component(rtc)
    except:
      pass
    return False
#
# 
def deactivate_rtc(path):
    try:
      rtc, ecs = get_ec(path)
      if ecs[0] :
        return ecs[0].deactivate_component(rtc)
    except:
      pass
    return False
#
# 
def reset_rtc(path):
    try:
      rtc, ecs = get_ec(path)
      if ecs[0] :
        return ecs[0].reset_component(rtc)
    except:
      pass
    return False
#
# 
def exit_rtc(path):
    try:
      rtc = resolve_rtc(path)
      if rtc :
        return rtc.exit()
    except:
      pass
    return False
#
# 
def list(val=''):
    if type(val) == type("") :
        return list_one(val)
    if type(val) == type([]) :
        res = []
        for x in val:
          res.append( list(x) )
        return res
    return ""
#
#
def list_one(val=''):
    global name_server
    try:
      root_context = name_server.root_context
      cxt = root_context
      cxt_str = val.split('/')
      for x in cxt_str:
          if x :
              if type(cxt.object_table[x][0]) == type(root_context) :
                  cxt = cxt.object_table[ x ][0]
              else:
                  return ""
      ll = cxt.object_table
      res = []
      for x in ll:
        if ll[x][1] == CosNaming.ncontext : res.append(val+x+"/")
        else: res.append(val+x)
      return res

    except:
      return ""
#
#
def get_rtc_ports(path):
  res = []
  try:
    rtc = resolve_rtc(path)
    ports = rtc.get_ports()
    for p in ports:
      prof = p.get_port_profile()
      res.append(prof.name) 
  except:
    pass
  return res
#
#
def check_connection(outp, inp):
  opp = outp.get_port_profile()
  for prof in op.connector_profiles:
    ports = prof.ports
    if len(pors) == 2 :
       if outp._is_equivalent(ports[0]) and inp._is_equivalent(ports[0]):
           return prof.connector_id
       elif inp._is_equivalent(ports[0]) and outp._is_equivalent(ports[0]):
           return prof.connector_id
  return None

def disconnect_ports(outp, inp):
    cid = check_connection(outp, inp)
    if cid :
      outp.disconnect(cid)
      return True
    return False

def get_rtc_port(path, pname):
  try:
    rtc = resolve_rtc(path)
    ports = rtc.get_ports()
    for p in ports:
      prof = p.get_port_profile()
      if prof.name.split('.')[-1] == pname:
          return p
  except:
    pass
  return None
 
    

##############################################
#    
def _setup(funcs=[], port=8080, global_var=globals()):
    global server

    signal.signal(signal.SIGINT, sig_int_handle)
    server = xmlrpc_server.SimpleXMLRPCServer(('localhost', port))
    funcs = [ _stop, initNS, getFunctions, getGlobals, registerFunction,remoteExec,list,activate_rtc, deactivate_rtc,reset_rtc,exit_rtc]
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

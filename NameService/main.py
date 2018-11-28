#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function
import sys
import os
import signal
from omniORB import CORBA,PortableServer

import CosNaming, CosNaming__POA
from impl import *

try:
    import SimpleXMLRPCServer as xmlrpc_server
except:
    import xmlrpc.server as xmlrpc_server


def create_names_poa(root_poa):
    try:
        names_poa = root_poa.find_POA("", False)
        return names_poa
    except:
        pl = root_poa.create_lifespan_policy(PortableServer.PERSISTENT)
        names_poa = root_poa.create_POA("", root_poa._get_the_POAManager(), [pl])
        names_poa._get_the_POAManager().activate()
        return names_poa
#
#
class NameService(object):
    def __init__(self, port=2809, with_setup=True):
        self.orb = None
        self.root_poa = None
        self.names_poa = None
        self.ins_poa = None
        self.root_context = None
        self.port = port
        if with_setup : self.setup()

    def setup(self):
        if not ('-ORBendPoint' in sys.argv) :
            sys.argv.append('-ORBendPoint')
            sys.argv.append('giop:tcp::'+str(self.port))
        
        sys.argv.append('-ORBpoaUniquePersistentSystemIds')
        sys.argv.append('1')

        self.orb = CORBA.ORB_init(sys.argv)
        self.root_poa = self.orb.resolve_initial_references("RootPOA")
        #
        #
        self.names_poa = create_names_poa(self.root_poa)
        #
        #
        self.ins_poa  = self.orb.resolve_initial_references("omniINSPOA")
        self.root_context = NamingContext_i("NameService", self.names_poa, self.ins_poa)
        self.ins_poa._get_the_POAManager().activate()
        #self.print_ior(self.root_context)
    #
    #
    def print_ior(self, obj):
        print(self.orb.object_to_string(obj._this()))
    #
    #
    def shutdown(self):
        try:
            self.shutdown_flag = False
            self.orb.shutdown(True)
        except:
            pass
        sys.exit()
    #
    #
    def mainloop(self, tv = 0.000001):
        if os.name == 'posix':
            self.orb.run()
        else:
            self.timeout = tv # 1 usec
            self.shutdown_flag = True
            self.shutdown_flag = self.orb._obj.run_timeout(self.timeout)
            try:
                while not self.shutdown_flag:
                    if self.timeout < 1.0:
                        self.timeout = self.timeout * 1.1
                    self.shutdown_flag = self.orb._obj.run_timeout(self.timeout)
            except:
                pass

    def run(self):
        #self.orb.run()
        self.mainloop()
        self.shutdown()

#
#
def daemonize(pidfname="NameService.pid"):
  try:
    pid=os.fork()
  except:
    print( "ERROR in fork1" )

  if pid > 0:
    os._exit(0)

  try:
    os.setsid()
  except:
    print( "ERROR in setsid" )

  try:
    pid=os.fork()
  except:
    print( "ERROR in fork2" )
  if pid > 0:
    with open(pidfname, "w") as f:
      print( pid, file=f )
    os._exit(0)

#
#
def main():
    ns = NameService()
    ns.run()

def name_server():
    import xmlrpc

    cmd='start'
    if 'stop' in sys.argv:
      cmd='stop'
      sys.argv.remove('stop')

    try:
        os.mkdir('/tmp/run')
    except:
        pass
    pid_file='/tmp/run/NameServer.pid'
    if len(sys.argv) > 1 and sys.argv:
        pid_file=sys.argv[1]

    if cmd == 'stop':
        if os.path.isfile(pid_file):
            stop_name_server(pid_file)
        else:   
            print("PID file not found")
        return
   
    if os.path.isfile(pid_file):
        print("NameServer is already running, remove %s" % pid_file)
        return

    if os.name == 'posix':
      daemonize(pid_file)
    xmlrpc.initNS()
    xmlrpc._setup()
    xmlrpc._start()
    try:
      os.remove(pid_file)
    except:
      pass

def stop_name_server(pid_file):
   pid=int(file(pid_file).read())
   os.kill(pid, signal.SIGINT)
   if os.path.isfile(pid_file):
     os.remove(pid_file)
    

if __name__ == '__main__':
    daemonize()
    main()

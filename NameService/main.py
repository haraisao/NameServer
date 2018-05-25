#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function
import sys
import os
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
        self.print_ior(self.root_context)
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

def main():
    ns = NameService()
    ns.run()

if __name__ == '__main__':
    main()

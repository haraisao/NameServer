#
#
from __future__ import print_function
import sys
from omniORB import CORBA,PortableServer

import CosNaming, CosNaming__POA
from NameService_impl import *

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
    def __init__(self):
        self.orb = None
        self.root_poa = None
        self.names_poa = None
        self.ins_poa = None
        self.root_context = None


    def setup(self):
        sys.argv.append('-ORBendPoint')
        sys.argv.append('giop:tcp::2809')
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

    def print_ior(self, obj):
        print(self.orb.object_to_string(obj._this()))
    
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


if __name__ == '__main__':
    ns = NameService()
    ns.setup()
    ns.run()

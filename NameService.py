#
#
from __future__ import print_function
import sys
from omniORB import CORBA,PortableServer

import CosNaming, CosNaming__POA
from NameService_impl import *

#
#
def orb_mainloop(orb):
    timeout = 0.000001 # 1 usec

    shutdown = orb._obj.run_timeout(timeout)
    try:
        while not shutdown:
            if timeout < 1.0:
                timeout = timeout * 1.1

            shutdown = orb._obj.run_timeout(timeout)
    except:
        pass

#
#
def main():
    sys.argv.append('-ORBendPoint')
    sys.argv.append('giop:tcp::2809')
    sys.argv.append('-ORBpoaUniquePersistentSystemIds')
    sys.argv.append('1')

    orb = CORBA.ORB_init(sys.argv)
    root_poa = orb.resolve_initial_references("RootPOA")
    pmon = root_poa._get_the_POAManager()

    #
    #
    pl = root_poa.create_lifespan_policy(PortableServer.PERSISTENT)
    names_poa = root_poa.create_POA("", pmon, [pl])
    names_poa._get_the_POAManager().activate()

    #
    #
    ins_poa  = orb.resolve_initial_references("omniINSPOA")

    root_context = NamingContext_i("NameService", ins_poa, names_poa)
    #obj = ins_poa.activate_object_with_id("NameService", root_context)
    ins_poa._get_the_POAManager().activate()

    print(orb.object_to_string(root_context._this()))
   
    orb.run()

    orb.shutdown()
    sys.exit()

if __name__ == '__main__':
    main()

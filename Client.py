#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function

from omniORB import CORBA, any, cdrUnmarshal, cdrMarshal
import CosNaming

import OpenRTM_aist
import RTC, OpenRTM, SDOPackage, RTM
from OpenRTM import CdrData, OutPortCdr, InPortCdr
from RTC import *


try:
    import xmlrpclib as xmlrpc_client
except:
    import xmlrpc.client as xmlrpc_client


client = xmlrpc_client.ServerProxy('http://localhost:8080')


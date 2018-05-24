#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function

try:
    import xmlrpclib as xmlrpc_client
except:
    import xmlrpc.client as xmlrpc_client


client = xmlrpc_client.ServerProxy('http://localhost:8080')


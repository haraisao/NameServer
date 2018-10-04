#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function
from NameService import *
import NameService.xmlrpc as xmlrpc
import sys

def initNS():
    return xmlrpc.initNS()

def main():
    xmlrpc.initNS()
    xmlrpc._setup()
    xmlrpc._start()
    #xmlrpc.name_server.run()

if __name__ == '__main__':
    if len(sys.argv) > 1:
      daemonize(sys.argv[1])
    else:
      daemonize()
    main()

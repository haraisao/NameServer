#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function
from NameService import *
import NameService.xmlrpc as xmlrpc

name_server = None

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

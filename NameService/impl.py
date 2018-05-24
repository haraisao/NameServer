#
#
# Copyright (C) 2018 Isao Hara, All Right Reserved.
# Released under the MIT license
#
from __future__ import print_function
from omniORB import URI
import CosNaming
import CosNaming__POA
import threading

''' 
  NameComponent -> {string, string}
  Name = [NameComponent,]
  BindingType(Enum) -> nobject, ncontext
  Binding -> { Name, BindingType }
  BindingList = [Binding]

 Interface: NamingContext, BindingIterator, NamingContextExt(NamingContext)

'''
from collections import OrderedDict

#
#  Interface NamingContextExt
#
class NamingContext_i(CosNaming__POA.NamingContextExt):
    '''
      NotFoundReason(Emun) -> missing_node, not_context, not_object
      exception NotFound{NotFoundReason, Name},
		 CannotProceed{NamingContext, Name},
		 InvalidName{}, AlreadyBound{}, NotEmpty{}
  
    '''
    def __init__(self, id, names_poa, ins_poa=None):
        if ins_poa:
            self.poa = ins_poa
        else:
            self.poa = names_poa

        self.iterators = {}
        self.binding_list = []
        self.object_table = OrderedDict()
        self.lock = threading.Lock()
        self.names_poa = names_poa

        if id is None:
            ref = self.poa.create_reference(CosNaming.NamingContext._NP_RepositoryId)
            self.id = self.poa.reference_to_id(ref)
        else:
            self.id = id
        try:
            self.poa.activate_object_with_id(self.id, self)
        except:
            pass
        #print ("Create NamingContext:", self.id)

    ##################################################
    #
    def get_next_context(self, n, force=False):
        key = URI.nameToString([n[0]])

        if self.object_table.has_key(key) :
            if self.object_table[key][1] == CosNaming.ncontext :
                return self.object_table[key][0]
            else:
                raise CosNamingContext.InvalidName()

        else:
           if force :
               nc = NamingContext_i(None, self.names_poa)
               self.object_table[key] = (nc, CosNaming.ncontext)
               return nc
           else:
               raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)            

    #
    #
    def bind_one(self, n, obj, force=False):
        if len(n) == 1:
            key = URI.nameToString(n)
            if not force and self.object_table.has_key(key):
                raise CosNaming.NamingContext.AlreadyBound()

            self.object_table[key] = (obj, CosNaming.nobject)
            return
        else:
            raise CosNaming.NamingContext.InvalidName()
        return

    ##################################################
    #
    # void bind (in Name n, in Object obj)
    #   raises (NotFound, CannotProceed, InvalidName, AlreadyBound);
    def bind(self, n, obj):
        if len(n) == 1:
            self.bind_one(n, obj, True)
            return
        else:
            cxt = self.get_next_context(n, True)
            cxt.bind(n[1:], obj)
        return
    #
    # void rebind (in Name n, in Object obj)
    #   raises (NotFound, CannotProceed, InvalidName);
    def rebind(self, n, obj):
        if len(n) == 1:
            self.bind_one(n, obj, True)
            return
        else:
            cxt = self.get_next_context(n, True)
            cxt.bind(n[1:], obj)
        return
    # 
    # void bind_context (in Name n, in NamingContext nc)
    #    raises (NotFound, CannotProceed,  InvalidName, AlreadyBound);
    def bind_context(self, n, nc, force=False):
        key = URI.nameToString(n)
        if not force and self.object_table.has_key(key) :
            raise CosNaming.NamingContext.AlreadyBound()

        self.object_table[key] = (nc, CosNaming.ncontext)
        return
    #
    # void rebind_context (in Name n, in NamingContext nc)
    #    raises (NotFound, CannotProceed, InvalidName);
    # (Not tested) 
    def rebind_context(self, n, nc):
        key = URI.nameToString(n)
        if self.object_table.has_key(key) :
            try:
                self.object_table[key][1].destroy()
            except e:
                raise e

            self.object_table[key] = (obj, CosNaming.ncontext)
        else:
            raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
        return
    #
    # Object resolve (in Name n)
    #    raises (NotFound, CannotProceed, InvalidName);
    def resolve(self, n):
        if len(n) == 1:
            key = URI.nameToString(n)
            if self.object_table.has_key(key) :
                if self.object_table[key][1] == CosNaming.nobject:
                    return self.object_table[key][0]
                elif self.object_table[key][1] == CosNaming.ncontext:
                    return self.object_table[key][0]._this()
                else:
                    raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
            else:
                raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
        else:
            pass
        return 
    #
    # void unbind (in Name n)
    #    raises (NotFound, CannotProceed, InvalidName);
    def unbind(self, n):
        if len(n) == 1:
            key = URI.nameToString(n)
            if self.object_table.has_key(key) :
                del self.object_table[key]
            else:
                pass
                #raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
        else:
            cxt = self.get_next_context(n)
            cxt.unbind(n[1:])
            pass
        return 
    #
    # NamingContext new_context ();
    # (Not tested)
    def new_context(self):
        nc = NamingContext_i(None, self.names_poa)
        ncref = nc._this()
        return ncref
    #
    # NamingContext bind_new_context (in Name n)
    #   raises (NotFound, CannotProceed, InvalidName, AlreadyBound);
    # (Not tested)
    def bind_new_context(self, n):
        nc = NamingContext_i(None, self.names_poa)
        ncref = nc._this()
        self.bind_context(n, nc)
        return ncref
    #
    # void destroy () raises (NotEmpty);
    def destroy(self):
        if len(self.naming_table) == 0 :
            for x in self.iterators:
                self.iterators[x].destroy() 
            id = self.pos.servant_to_id(self)
            self.poa.deactivate_object(id)
        else:
            raise CosNaming.NamingContext.NotEmpty()
        return 
    #
    # void list (in unsigned long how_many,
	#       out BindingList bl, out BindingIterator bi);
    def list(self, how_many):
        rest = None
        bl = []
        for i,x in enumerate(self.object_table):
            if i < how_many:
                name = URI.stringToName(x)
                val = CosNaming.Binding(name, self.object_table[x][1])
                bl.append(val)
            else:
                rest = self.object_table.keys()[how_many:]
    
        if rest:
            bii = BindingIterator_i(self, self.names_poa, rest)
            id = self.names_poa.activate_object(bii)
            bi = self.names_poa.id_to_reference(id)
            self.lock.acquire()
            self.iterators[id] = bii
            self.lock.release()
        else:
            bi = None
        return (bl, bi)
    #
    #  StringName  to_string(in Name n)      raises(InvalidName);
    def to_string(self, n):
        return URI.nameToString(n)
    #
    # Name        to_name(in StringName sn) raises(InvalidName);
    def to_name(self, sn):
        return URI.stringToName(sn)
    #
    # URLString   to_url(in Address addr, in StringName sn)
    #   raises(InvalidAddress, InvalidName);
    def to_url(self, addr, sn):
        return URI.addrAndNameToURI(addr, sn)
    #
    # Object      resolve_str(in StringName n)
    #  raises(NotFound, CannotProceed, InvalidName, AlreadyBound);
    def resolve_str(self, sn):
        return self.resolve(URI.stringToName(sn))
    
    ###############################################################
    # for BindingIterator
    def _removeIterator(self, id):
        self.lock.acquire()
        del self.iterators[id]
        self.lock.release()
        return
        
###################################################################
# Interface: BindingIterator
#
class BindingIterator_i(CosNaming__POA.BindingIterator):
    def __init__(self, nc, poa, keys):
        self.name_context = nc
        self.poa = poa
        self.keys = keys
        self.object_table = nc.object_table
        #print("BindingIterator created")

    def __del__(self):
        #print("BindingIterator deleted")
        pass

    # boolean next_one (out Binding b);
    def next_one(self):
        b = None
        res = True
        try:
          x = self.keys.pop(0)
          name = URI.stringToName(x)
          b = CosNaming.Binding(name, self.object_table[x][1])
        except:
          res = False
          self.destroy()
        return (res, b)

    # boolean next_n   (in unsigned long how_many, out BindingList bl);
    def next_n(self, how_many):
        res = True
        bl = []
        try:
          n_keys = len(self.keys)
          for i in range(n_keys):
            if i < how_many:
                x = self.keys.pop(0)
                name = URI.stringToName(x)
                val = CosNaming.Binding(name, self.object_table[x][1])
                bl.append(val)
        except:
          res = False
          self.destroy()
        return (res, bl)

    # void    destroy  ();
    def destroy(self):
        id = self.poa.servant_to_id(self)
        self.name_context._removeIterator(id)
        self.poa.deactivate_object(id)
        return



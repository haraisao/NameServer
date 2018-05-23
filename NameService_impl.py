#
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


'''

class BindingItem(object):
    def __init__(self, name, typ, obj):
        self.name = name
        self.name_str = URI.nameToString(name)
        self.object = obj
        self.type = typ

    def compare(self, name):
        return self.name_str == URI.nameToString(name)

    def get(self):
        return CosNaming.Binding(self.name, self.type)


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
        self.naming_table = {}
        self.context_table = {}
        self.binding_list = []
        self.object_table = {}
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
        print ("Create NamingContext:", self.id)

    ##################################################
    #
    def get_next_context(self, n, force=False):
        print("Call get_next_content", n)
        key = URI.nameToString([n[0]])
        if self.object_table.has_key(key) :
            raise CosNaming.NamingContext.InvalidName()

        if self.object_table.has_key(key) :
            if self.object_table[key][1] == CosNaming.ncontext :
                return self.object_table[key][0]
            else:
                raise CosNamingContext.InvalidName()

        else:
           if force :
               nc = NamingContext_i(None, self.names_poa)
               self.binding_list.append(BindingItem([n[0]], CosNaming.ncontext, nc))
               self.object_table[key] = (nc, CosNaming.ncontext)
               return nc
           else:
               raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)            

    #
    #
    def bind_one(self, n, obj, force=False):
        print("Call bind_one", n)
        if len(n) == 1:
            self.binding_list.append(BindingItem(n, CosNaming.nobject, obj))
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
    def bind(self, n, obj):
        print("Call bind")
        if len(n) == 1:
            self.bind_one(n, obj, True)
            return
        else:
            cxt = self.get_next_context(n, True)
            cxt.bind(n[1:], obj)
        return
    #
    def rebind(self, n, obj):
        if len(n) == 1:
            self.bind_one(n, obj, True)
            return
        else:
            cxt = self.get_next_context(n, True)
            cxt.bind(n[1:], obj)
        return 

    #
    def bind_context(self, n, nc):
        print("Call bind_context")
        
        key = URI.nameToString(n)
        if not force and self.object_table.has_key(key) :
            raise CosNaming.NamingContext.AlreadyBound()

        self.context_table[key] = (nc, CosNaming.ncontext)
        return

    #
    def rebind_context(self, n, nc):
        key = URI.nameToString(n)
        if self.object_table.has_key(key) :
            try:
                self.object_table[key][1].destroy()
            except e:
                raise e

            self.object_table[key] = (obj, CosNaming.nobject)
        else:
            raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
        return
    #
    def resolve(self, n):
        print("Call resolve", n)
        if len(n) == 1:
            key = URI.nameToString(n)
            if self.object_table.has_key(key) :
                if self.object_table[key][1] == CosNaming.nobject:
                    return self.object_table[key][0]
                elif self.object_table[key][1] == CosNaming.ncontext:
                    return object_table[key][0]._this()
                else:
                    raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
            else:
                raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
        else:
            pass
        return 
    #
    def unbind(self, n):
        print("Call unbind", n)
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

    def new_context(self):
        nc = NamingContext_i(None, self.names_poa)
        ncref = nc._this()
        return ncref

    def bind_new_context(self, n):
        return None

    def destroy(self):
        if len(self.naming_table) == 0 :
            for x in self.iterators:
                self.iterators[x].destroy() 
            id = self.pos.servant_to_id(self)
            self.poa.deactivate_object(id)
        else:
            raise CosNaming.NamingContext.NotEmpty()
        return 

    def list(self, how_many):
        print("Call list")
        rest = None
        bl = []
        for i,x in enumerate(self.object_table):
            if i < how_meny:
                name = URI.stringToName(x)
                val = CosNaming.Binding(name, self.object_table[x][1])
                bl.append(val)
            else:
                break
    
        if rest:
            bii = BindingIterator_i(self, self.names_poa, rest)
            id = self.names_poa.activate_object(bii)
            bi = self.names_poa.id_to_reference(id)
            self.lock.acquire()
            self.iterators[id] = bii
            self.lock.release()
        else:
            bi = None
        print(bl, bi)
        return (bl, bi)

    def to_string(self, n):
        return URI.nameToString(n)

    def to_name(self, sn):
        return URI.stringToName(sn)

    def to_url(self, addr, sn):
        return URI.addrAndNameToURI(addr, sn)

    def resolve_str(self, sn):
        return self.resolve(URI.stringToName(sn))

    def _removeIterator(self, id):
        self.lock.acquire()
        del self.iterators[id]
        self.lock.release()
        return
#
#
class BindingIterator_i(CosNaming__POA.BindingIterator):
    def __init__(self, nc, poa, bindings):
        self.name_context = nc
        self.poa = poa
        self.bindings = bindings
        print("BindingIterator created")

    def __del__(self):
        print("BindingIterator deleted")

    def nect_one(self):
        return

    def next_n(self, how_many):
        return

    def destroy(self):
        id = self.pos.servant_to_id(self)
        self.name_context._removeIterator(id)
        self.poa.deactivate_object(id)



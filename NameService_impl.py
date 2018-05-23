#
#
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
class NamingContext_i(CosNaming__POA.NamingContextExt):
    '''
      NotFoundReason(Emun) -> missing_node, not_context, not_object
      exception NotFound{NotFoundReason, Name}, CannotProceed{NamingContext, Name}, InvalidName{}, AlreadyBound{}, NotEmpty{}
  
    '''
    def __init__(self, name, poa,names_poa):
        self.poa = poa
        self.iterators = {}
        self.naming_table = {}
        self.lock = threading.Lock()
        self.iterator_poa = names_poa
        self.name = name
        if name:
            poa.activate_object_with_id(name, self)

        print ("Create NamingContext:"+name)

    def bind(self, n, obj):
        if len(n) == 1:
            if self.naming_table.has_key(n[0]) :
                raise CosNaming.NamingContext.AlreadyBound()
                return
            self.naming_table[n[0]] = obj
            return
        else:
            pass
        return

    def rebind(self, n, obj):
        if len(n) == 1:
            if self.naming_table.has_key(n[0]) :
                self.naming_table[n[0]] = obj
            else:
                raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
        else:
            pass
        return 

    def bind_context(self, n, nc):
        if self.naming_table.has_key(n) :
            raise CosNaming.NamingContext.AlreadyBound()
            return
        self.naming_table[n] = nc
        return

    def rebind_context(self, n, nc):
        if self.naming_table.has_key(n) :
            try:
                self.naming_table[n].destroy()
            except e:
                raise e
                return
            self.naming_table[n] = obj
        else:
            raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
        return

    def resolve(self, n):
        if len(n) == 1:
            if self.naming_table.has_key(n[0]) :
                return self.naming_table[n[0]]
            else:
                raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
        else:
            pass
        return 

    def unbind(self, n):
        if len(n) == 1:
            if self.naming_table.has_key(n[0]) :
                del self.naming_table[n[0]]
            else:
                raise CosNaming.NamingContext.NotFound(CosNaming.NamingContext.missing_node, n)
        else:
            pass
        return 

    def new_context(self):
        return 

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
        rest = None
        bl = []
        for x in self.naming_table:
            bl = [CosNaming.Binding([name], CosNaming.nobject),]
        if rest:
            bii = BindingIterator_i(self, self.iterator_poa, rest)
            id = self.iterator_poa.activate_object(bii)
            bi = self.iterator_poa.id_to_reference(id)
            self.lock.acquire()
            self.iterators[id] = bii
            self.lock.release()
        else:
            bi = None
        return (bl, bi)

    def to_string(self, *args):
        return 

    def to_name(self, *args):
        return 

    def to_url(self, *args):
        return

    def resolve_str(self, *args):
        return 

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



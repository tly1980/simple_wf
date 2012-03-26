
class MultiEntryReturn(Exception):
	pass

class InvalidEntry(Exception):
	pass

class EntryAlreadyActivated(Exception):
    pass

class PersistentDriver(object):

    def __init__(self, instance_id):
        self.instance_id = instance_id


    def activate(entries_input):
        pass

    def complete(entry):
        pass

    def activated_set(self):
        pass

    def completed_set(self, is_4_routing_eval = False):
        pass

    def disable_andjoin(self, set_in):
        pass

class MemPersistentDriver(object):
    """docstring for MemPersistentDriver"""
    def __init__(self, instance_id):
        super(MemPersistentDriver, self).__init__()
        self.a_set = set([])
        self.c_set = set([])
        self.c_set_4_routing_eval = set([])

    def activate(entries_input):
        entries_input = set(entries_input)
        inter_set = self.a_set.intersection()
        if len(inter_set) > 0:
            raise EntryAlreadyActivated()
        
        

    def complete(entry):
        pass

    def activated_set(self):
        pass

    def completed_set(self, is_4_routing_eval = False):
        pass

    def disable_andjoin(self, set_in):
        pass
     

class WorkflowEngine(object):
	def __init__(self, p_driver, router):
		self.p_driver = p_driver
        self.router = router
	
    def router(self, router = None):
        if router is None:
            return self.router
        
    def start(self):

    	self.p_driver.activate('_new')
    	self.complete('_new')

    def complete(self, entry, data = None, comments = None):
    	if entry not in self.p_driver.active_entries():
    		raise InvalidEntry()

    	entries = set([])
    	entries.update(self.p_driver.completed_set(True))
    	entries.add(entry)
        self.p_driver.complete(entry)

    	for r in self.match_routes(entries, data):
            entries_input = r.input().entries
            entries_output = r.ouput().choices()
            self.p_driver.activate(entries_input, entries_output)
            self.p_driver.disable_andjoin(entries_input)


    def todo_set(self):
        ret = p_driver.activated_set()
        if len(ret) == 0:
            return set(['_new'])

        return ret
        
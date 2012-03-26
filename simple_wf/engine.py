
class MultiEntryReturn(Exception):
	pass

class InvalidEntry(Exception):
	pass

class PersistentDriver(object):

    def activate(entry):
        pass

    def complete(entry):
        pass

    def activated_set(self):
        pass

    def completed_set(self):
        pass

    def completed_set_routing_eval(self):
        pass

    def disable_andjoin(self, set_in):
        pass

class WorkflowEngine(object):
	def __init__(self, p_driver):
		self.p_driver = p_driver
		
    def config(self, router):
        self.router = router

    def start(self):
    	self.p_driver.activate('_new')
    	self.complete('_new')


    def complete(self, entry, data = None, comments = None):
    	if entry not in self.p_driver.active_entries():
    		raise InvalidEntry()

    	entries = set([])
    	entries.update(self.p_driver.completed_list_andjoin())
    	entries.add(entry)
    	ret = router.match(entries, data)
    	if len(ret) > 1:
    		raise MultiEntryReturn()

    	e = ret[0]
    	self.p_driver.activate(e, data, comments)


    def todo_set(self):
        ret = p_driver.active_set()
        if len(ret) == 0:
            return set(['_new'])

        return ret
        
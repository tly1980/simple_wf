
class MultiEntryReturn(Exception):
	pass

class InvalidEntry(Exception):
	pass

class WorkflowEngine(object):
	def __init__(self, p_driver):
		self.p_driver = p_driver
		

    def config(self, router):
        self.router = router

    def start(self):
    	self.p_driver.activate('_new')
    	self.complete('_new')

    def choices(self):
    	return self.p_driver.active_entries()	

    def active_entries(self):
    	return self.p_driver.active_entries()

    def complete(self, entry, data = None, comments = None):
    	if entry not in self.p_driver.active_entries():
    		raise InvalidEntry()

    	entries = set([])
    	entries.update(self.p_driver.active_entries())
    	entries.add(entry)
    	ret = r.match(entries, data)
    	if len(ret) > 1:
    		raise MultiEntryReturn()

    	e = ret[0]
    	self.p_driver.activate(e, data, comments)

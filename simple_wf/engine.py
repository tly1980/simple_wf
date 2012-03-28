from .exception import EntryNotActivated


class WorkflowEngine(object):
    def __init__(self, p_driver, router):
        self.p_driver = p_driver
        self._router = router

    def router(self, router=None):
        if router is None:
            return self._router
        self._router = router
        return self

    def start(self):
        self.p_driver.activate(['_new'])
        self.complete('_new')

    def complete(self, entry, data=None, comments=None):
        activated_set = self.p_driver.activated_set()
        if entry not in activated_set:
            raise EntryNotActivated(entry)

        #remove the involve activate set
        set_to_retired = set([])
        for e in self._router.involve_decendants(entry):
            if e in activated_set:
                set_to_retired.add(e)

        if entry in set_to_retired:
            set_to_retired.remove(entry)

        self.p_driver.retired_actived_set(set_to_retired)

        entries = set([])
        entries.update(self.p_driver.completed_set(True))
        entries.add(entry)

        if entry in self._router.entries_involves_andjoin():
            self.p_driver.complete(entry, True)
        else:
            self.p_driver.complete(entry, False)

        for r in self._router.match_routes(entries, data):
            entries_input = r.input().entries
            entries_output = r.output().choices()
            self.p_driver.activate(entries_output)
            self.p_driver.disable_andjoin(entries_input)

    def todo_set(self):
        ret = self.p_driver.activated_set()
        return ret

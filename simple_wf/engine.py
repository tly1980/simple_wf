from datetime import datetime


class EntryException(Exception):
    def __init__(self, *args, **kwargs):
        self.entry_set = set([])
        self.entry_set.update(*args)
        entry_set = kwargs.get('entry_set')
        if entry_set:
            self.entry_set.update(entry_set)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, repr(self.entry_set))


class MultiEntryReturn(EntryException):
    pass


class InvalidEntry(EntryException):
    pass


class EntryAlreadyActivated(EntryException):
    pass


class EntryNotActivated(EntryException):
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

    def completed_list(self, is_4_routing_eval=False):
        pass

    def disable_andjoin(self, set_in):
        pass

    def retired_actived_set(self, set_in):
        pass


class MemPersistentDriver(object):
    """docstring for MemPersistentDriver"""
    def __init__(self, instance_id):
        super(MemPersistentDriver, self).__init__()
        self.a_list = []
        self.c_list = []
        self.history = []

    def activated_set(self):
        return set(map(lambda a: a['e'], self.a_list))

    def activate(self, entries_input):
        entries_input = set(entries_input)
        a_list = map(lambda a: a['e'], self.a_list)
        inter_set = entries_input.intersection(a_list)
        if len(inter_set) > 0:
            raise EntryAlreadyActivated(entry_set=inter_set)

        for e in entries_input:
            self.a_list.append({'e': e, 'timestamp_a': datetime.now()})

    def complete(self, entry, is_4_routing_eval=False):
        if entry not in self.activated_set():
            raise EntryNotActivated(entry)

        self.c_list.append({
            'e': entry,
            'timestamp_c': datetime.now(),
            'is_4_routing_eval': is_4_routing_eval
        })

        self.a_list = filter(lambda e: e['e'] != entry, self.a_list)

    def completed_set(self, is_4_routing_eval=False):
        f_lst = filter(lambda e: e['is_4_routing_eval'] == is_4_routing_eval, self.c_list)
        ret = set(map(lambda e: e['e'], f_lst))
        return ret

    def disable_andjoin(self, set_in):
        for e in self.c_list:
            if e['e'] in set_in:
                e['is_4_routing_eval'] = False

    def retired_actived_set(self, set_in):
        self.a_list = filter(lambda e: e['e'] not in set_in, self.a_list)


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

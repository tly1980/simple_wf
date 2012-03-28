from .exception import EntryAlreadyActivated, EntryNotActivated
from datetime import datetime


class PersistentDriver(object):
    def __init__(self, instance_id):
        self.instance_id = instance_id

    def activate(self,  *args, **kwargs):
        pass

    def complete(self, entry):
        pass

    def activated_set(self):
        pass

    def completed_list(self, is_4_routing_eval=False):
        pass

    def disable_andjoin(self, set_in):
        pass

    def retired_actived(self, set_in):
        pass

    def close_wf(self):
        pass

    def open_wf(self):
        pass

    def cancel_wf(self):
        pass

    def log_transition(input, output):
        pass


class MemPersistentDriver(PersistentDriver):
    """docstring for MemPersistentDriver"""
    def __init__(self, instance_id):
        super(MemPersistentDriver, self).__init__(instance_id)
        self.a_list = []
        self.c_list = []
        self.history = []

    def activated_set(self):
        return set(map(lambda a: a['e'], self.a_list))

    def activate(self,  *args, **kwargs):
        entries = kwargs.get('entries', set([]))
        entries = set(entries)
        for a in args:
            entries.add(a)

        a_list = map(lambda a: a['e'], self.a_list)
        inter_set = entries.intersection(a_list)
        if len(inter_set) > 0:
            raise EntryAlreadyActivated(entry_set=inter_set)

        for e in entries:
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

    def retired_actived(self, set_in):
        self.a_list = filter(lambda e: e['e'] not in set_in, self.a_list)

class EntryException(Exception):
    def __init__(self, *args, **kwargs):
        super(EntryException, self).__init__()
        self.entry_set = set([])
        self.entry_set.update(args)

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

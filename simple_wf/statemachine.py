import string


class EntryMatcher(object):
    def __init__(self, *args, **kwargs):
        self.entries = set()
        for s in args:
            self.entries.add(s)

    def match(self, entries):
        raise Exception, 'Implement me!'

    def __repr__(self):
        return '%s:%s' % (self.__class__.__name__, repr(list(self.entries)))

    def __iter__(self):
        return self.entries.__iter__()

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.entries == other.entries

    def __ne__(self, other):
        if self.__class__ != other.__class__:
            return True

        return self.entries != other.entries


'''
Input for activities
'''


class Exact(EntryMatcher):
    def match(self, entries):
        #return True, that means entries must be the subsets of self.entries.
        if self.entries.issubset(entries):
            return True
        return False


class Any(EntryMatcher):
    def match(self, entries):
        if self.entries.isdisjoint(entries):
            return False
        else:
            return True


'''
Output for activities
'''


class Next(object):
    def __init__(self, *args, **kwarg):
        self._choices = set([])
        for s in args:
            self._choices.add(s)

    def choices(self):
        return self._choices

    def __repr__(self):
        return '%s:%s' % (self.__class__.__name__, repr(list(self._choices)))


def always_pass(test_data=None):
    return True


class Route(object):
    def __init__(self):
        self.test_fun = always_pass
        self._in = None
        self._out = None

    def is_andjoin(self):
        if not isinstance(self.input(), Exact):
            return False

        if len(self.input().entries) < 2:
            return False

        return True

    def is_andsplit(self):
        if len(self.output().choices()) > 1:
            return True
        return False

    def input(self, the_in=None):
        if the_in is not None:
            self._in = the_in
            return self
        else:
            return self._in

    def any(self, *args, **kwargs):
        self._in = Any(*args)
        return self

    def exact(self, *args, **kwargs):
        self._in = Exact(*args)
        return self

    def next(self, *args, **kwargs):
        self._out = Next(*args)
        return self

    def __repr__(self):
        return 'in: %s, out: %s' % (self._in, self._out)

    def output(self, the_out=None):
        if the_out is not None:
            self._out = the_out
            return self
        else:
            return self._out

    def involves(self, entry):
        if entry in self._in:
            return True
        return False

    def match_entry(self, entries):
        return self._in.match(entries)

    def match_data(self, data):
        return self.test_fun(data)

    def match(self, entries, data):
        return self.match_entry(entries) and self.match_data(data)

    def test(self, test_fun=None):
        if test_fun is None:
            return self.test_fun
        self.test_fun = test_fun
        return self


class Router(object):
    def __init__(self, *args, **kwargs):
        self.routes = []
        for r in args:
            self.routes.append(r)

    def match_entry(self, entries):
        ret = set()
        for r in self.routes:
            if r.match_entry(entries):
                ret.update(r.output().choices())
        return ret

    def match(self, entries, data=None):
        ret = set([])
        for r in self.match_routes(entries, data):
            ret.update(r.output().choices())
        return ret

    def match_routes(self, entries, data=None):
        ret = []
        for r in self.routes:
            if r.match(entries, data):
                ret.append(r)
        return ret

    def involve_decendants(self, entry, ret=None):
        if ret is None:
            ret = set([])

        for r in self.routes:
            if r.involves(entry):
                nexts = r.output().choices()
                s_diff = nexts.difference(ret)
                if len(s_diff):
                    ret.update(s_diff)
                for s in s_diff:
                    self.involve_decendants(s, ret)
        return ret

    def choices(self, entry):
        ret = set([])
        for r in self.routes:
            if r.match_entry([entry]):
                ret.update(r.output().choices())

        return ret

    '''
    Return the entry that can generate the join result.
    '''
    def entries_involves_andjoin(self):
        ret = set([])
        for r in self.routes:
            if r.is_andjoin():
                ret.update(r.input().entries)

        return ret

    '''
    Return the entry that will produce split result.
    '''
    def entries_involves_andsplit(self):
        ret = set([])
        for r in self.routes:
            if r.is_andsplit():
                ret.update(r.output().choices())

        return ret

    def __repr__(self):
        l = []
        for r in self.routes:
            l.append(repr(r))

        return string.join(l, '\n')

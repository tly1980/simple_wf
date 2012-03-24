import string
class DoNothingApp(object):
    def do(in_data):
        return in_data

class ActivityCfg(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name')
        self.app = kwargs.get('app', DoNothingApp())

class Activity(object):
    def __init__(self, *args, **kwargs):
        self.activity_cfg = kwargs.get('activity_cfg')
        self.state = kwargs.get('state')

    def app_run(in_data):
        self.out_data = self.activity_cfg.do(in_data)
        return self.out_data

    def activate():
        self.state = 'activated'

    def complete():
        self.state = 'completed'

class StepMatcher(object):
    
    def __init__(self, *args, **kwargs):
        self.steps = set()
        for s in args:
            self.steps.add(s)
        

    def match(self, steps):
        raise Exception, 'Implement me!'

    def __repr__(self):
        return '%s:%s' % ( self.__class__.__name__ , repr ( list(self.steps)) )

    def __iter__(self):
        return self.steps.__iter__()

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.steps == other.steps

    def __ne__(self, other):
        if self.__class__ != other.__class__:
            return True

        return self.steps != other.steps

        

    
'''
Input for activities
'''
class Exact(StepMatcher):
    def match(self, steps):
        #return True, that means steps must be the subsets of self.steps.
        if self.steps.issubset(steps):
            return True
        return False
        

class Any(StepMatcher):
    def match(self, steps):
        if self.steps.isdisjoint(steps):
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
        return '%s:%s' % ( self.__class__.__name__ , repr ( list( self._choices)) )

def always_pass(test_data=None):
    return True


class Route(object):

    def __init__(self):
        self.test_fun = always_pass
        self._in = None
        self._out = None


    def input( self, the_in = None):
        if the_in is not None:
            self._in= the_in
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

    def output(self, the_out = None):
        if the_out is not None:
            self._out = the_out
            return self
        else:
            return self._out

    def involves(self, step):
        if step in self._in:
            return True
        return False

    def match_step(self, steps):
        return self._in.match(steps)

    def match_data(self, data):
        return self.test_fun(data)

    def match(self, steps, data):
        return self.match_step(steps) and self.match_data(data)

    def test(self, test_fun=None):
        if test_fun is None:
            return self.test_fun
        self.test_fun = test_fun
        return self


class RouteMatcher(object):
    
    def __init__(self, *args, **kwargs):
        self.routes = []
        for r in args:
            self.routes.append(r)

    def match_step(self, steps):
        ret = set()
        for r in self.routes:
            if r.match_step(steps):
                ret.update(r.output().choices())
        return ret

    def match(self, steps, data = None):
        ret = set()
        for r in self.routes:
            if r.match(steps, data):
                ret.update(r.output().choices())
        return ret

    def involve_decendants(self, step, ret=set([])):
        for r in self.routes:
            if r.involves( step ):
                nexts = r.output().choices()
                s_diff = nexts.difference(ret)
                if len(s_diff):
                    ret.update(s_diff)
                for s in s_diff:
                    ret2 = self.involve_decendants(s, ret)
        return ret

    def choices(self, step):
        ret = set([])
        for r in self.routes:
            if r.match_step([step]):
                ret.update(r.output().choices())

        return ret

    def __repr__(self):
        l = []
        for r in self.routes:
            l.append(repr(r))

        return string.join(l, '\n')


        
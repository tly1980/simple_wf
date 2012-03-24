"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from warehouse.wf.statemachine import Route, RouteMatcher, Any, Next, All

class RouterMatcherTest(TestCase):
    matcher = None

    def out_should_exact_match(self, set_in, set_expect):
        set_in = set(set_in)
        set_expect = set(set_expect)
        out = self.matcher.match_step( set_in )

        if out != set_expect:
            msg_show = ' matcher:\n %s,\n ------ \n in:%s, out: %s \n expect: %s' % (self.matcher, set_in, out, set_expect )
            self.fail(msg_show)

    def out_should_not_match(self, set_in, set_expect):
        set_in = set(set_in)
        set_expect = set(set_expect)
        out = self.matcher.match_step( set_in )

        if out == set_expect:
            msg_show = ' matcher:\n %s,\n ------ \n in:%s, out: %s \n expect: %s' % (self.matcher, set_in, out, set_expect )
            self.fail(msg_show)
        

    def test_wf_match_step(self):
        matcher = RouteMatcher(
            Route().input( Any('_new') ).output( Next('step1') ),
            Route().input( Any('step1') ).output( Next('step2') ),
            Route().input( Any('step2') ).output( Next('step3') ),
            Route().input( Any('step3') ).output( Next('end') ),
        )

        self.assertEquals( matcher.match_step(['_new']), set(['step1']) )
        self.assertEquals( matcher.match_step(['step1']), set(['step2']) )
        self.assertEquals( matcher.match_step(['step2']), set(['step3']) )
        self.assertEquals( matcher.match_step(['step3']), set(['end']) )


    def test_wf_multi_out(self):
        matcher = RouteMatcher(
            Route().input( Any('_new') ).output( Next('step1', 'step1.1', 'step1.2') ),
            Route().input( Any('step1') ).output( Next('step2', 'step2.1') ),
            Route().input( Any('step1.1') ).output( Next('step2', 'end') ),
            Route().input( Any('step1.2') ).output( Next('step2.1', 'end') ),
            Route().input( Any('step2') ).output( Next('end') ),
            Route().input( Any('step2.1') ).output( Next('end') ),
        )

        self.assertEquals( matcher.match_step(['_new']), 
                            set(['step1', 'step1.1', 'step1.2']) )
        self.assertEquals( matcher.match_step(['step1']), 
                            set(['step2.1', 'step2']))
        self.assertEquals( matcher.match_step(['step1.1']), 
                            set(['step2', 'end']) )
        self.assertEquals( matcher.match_step(['step1.2']), 
                            set(['step2.1', 'end']) )
        self.assertEquals( matcher.match_step(['step2']), 
                            set(['end']))
        self.assertEquals( matcher.match_step(['step2.1']), 
                            set(['end']))


    def test_wf_multi_in_all(self):
        matcher = RouteMatcher(
            Route().input( Any('_new') ).output( Next('step1', 'step1.1', 'step1.2', 'step1.3') ),
            Route().input( All('step1.1', 'step1.2') ).output( Next('step2') ),
            Route().input( Any('step1', 'step1.3') ).output( Next('step2') ),
            Route().input( Any('step2') ).output( Next('end') ),
        )

        self.assertEquals( matcher.match_step( ['_new']), set(['step1', 'step1.1', 'step1.2', 'step1.3']) )
        self.assertEquals( matcher.match_step( ['step1.1', 'step1.2'] ), set(['step2']))
        self.assertEquals( matcher.match_step( ['step1.3'] ), set(['step2']) )
        self.assertEquals( matcher.match_step( ['step1'] ), set(['step2']) )
        self.assertEquals( matcher.match_step( ['step2'] ), set(['end']) )


        self.assertEquals( matcher.match( ['_new']), set(['step1', 'step1.1', 'step1.2', 'step1.3']) )
        self.assertEquals( matcher.match( ['step1.1', 'step1.2'] ), set(['step2']))
        self.assertEquals( matcher.match( ['step1.3'] ), set(['step2']) )
        self.assertEquals( matcher.match( ['step1'] ), set(['step2']) )
        self.assertEquals( matcher.match( ['step2'] ), set(['end']) )


    def test_wf_match(self):
        matcher = RouteMatcher(
            Route().input( Any('_new') ).output( Next('check') ),
            Route().input( Any('check') ).output( Next('not_pass') ).test( lambda d: d.get('score') < 60  ),
            Route().input( Any('check') ).output( Next('pass') ).test( lambda d: d.get('score') >= 60 ),
        )

        self.assertEquals( matcher.match( ['check'], {'score': 60}), set(['pass']) )
        self.assertEquals( matcher.match( ['check'], {'score': 100}), set(['pass']) )
        self.assertEquals( matcher.match( ['check'], {'score': 59}), set(['not_pass']) )
        self.assertEquals( matcher.match( ['check'], {'score': -60}), set(['not_pass']) )

    def test_involves_decendants(self):
        matcher = RouteMatcher(
            Route().input( Any('_new') ).output( Next('check') ),
            Route().input( Any('parent') ).output( Next('childA', 'childB') ),
            Route().input( Any('childA') ).output( Next('childA.1') ),
            Route().input( Any('childA.1') ).output( Next('childA.2', 'childAA.1') ),
            Route().input( Any('childB') ).output( Next('childB.1') ),
            Route().input( Any('childB.1') ).output( Next('childB.2', 'childBB.1') ),
        )
        import ipdb; ipdb.set_trace()
        s = matcher.involve_decendants('parent')
        print s
        

class StepMatcherTest(TestCase):

    def test_iterator(self):
        any = Any('a', 'b', 'c')
        i = 0

        l = ['a', 'b', 'c']

        for s in any:
            self.assertTrue( s in l )
            l.remove(s)

        self.assertEquals( len(l), 0 )
        



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
        
        

    def test_wf_single_out(self):
        self.matcher = RouteMatcher(
            Route().input( Any('start') ).output( Next('step1')  ),
            Route().input( Any('step1') ).output( Next('step2')  ),
            Route().input( Any('step2') ).output( Next('step3') ),
            Route().input( Any('step3') ).output( Next('end') ),
        )

        self.out_should_exact_match( ['start'], ['step1'])
        self.out_should_exact_match( ['step1'], ['step2'])
        self.out_should_exact_match( ['step2'], ['step3'])
        self.out_should_exact_match( ['step3'], ['end'])


        self.out_should_not_match( ['start'], ['start'])
        self.out_should_not_match( ['start'], ['step2'])
        self.out_should_not_match( ['start'], ['step3'])
        self.out_should_not_match( ['start'], ['end'])
        
    def test_wf_multi_out(self):
        self.matcher = RouteMatcher(
            Route().input( Any('start') ).output( Next('step1', 'step1.1', 'step1.2')),
            Route().input( Any('step1') ).output( Next('step2', 'step2.1')),
            Route().input( Any('step1.1') ).output( Next('step2', 'end')),
            Route().input( Any('step1.2') ).output( Next('step2.1', 'end')),
            Route().input( Any('step2') ).output( Next('end') ),
            Route().input( Any('step2.1') ).output( Next('end') ),
        )

        self.out_should_exact_match( ['start'], ['step1', 'step1.1', 'step1.2'])
        self.out_should_exact_match( ['step1'], ['step2.1', 'step2'])
        self.out_should_exact_match( ['step1.1'], ['step2', 'end'])
        self.out_should_exact_match( ['step1.2'], ['step2.1', 'end'])
        self.out_should_exact_match( ['step2'], ['end'])
        self.out_should_exact_match( ['step2.1'], ['end'])


    def test_wf_multi_in_all(self):
        self.matcher = RouteMatcher(
            Route().input( Any('start') ).output( Next('step1', 'step1.1', 'step1.2', 'step1.3')),
            Route().input( All('step1.1', 'step1.2') ).output( Next('step2')),
            Route().input( Any('step1', 'step1.3') ).output( Next('step2')),
            Route().input( Any('step2') ).output( Next('end')),
        )

        self.out_should_exact_match( ['start'], ['step1', 'step1.1', 'step1.2', 'step1.3'])
        self.out_should_exact_match( ['step1.1', 'step1.2'], ['step2'])
        self.out_should_exact_match( ['step1.3'], ['step2'])
        self.out_should_exact_match( ['step1'], ['step2'])
        self.out_should_exact_match( ['step2'], ['end'])

        print self.matcher



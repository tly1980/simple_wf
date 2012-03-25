"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from warehouse.wf.statemachine import Route, Router, Any, Exact, Next

class RouterMatcherTest(TestCase):

    def test_wf_match_entry(self):
        router = Router(
            Route().any('_new').next('e1'),
            Route().any('e1').next('e2'),
            Route().any('e2').next('e3'),
            Route().any('e3').next('_end'),
        )


        self.assertEquals( router.match_entry(['_new']), set(['e1']) )
        self.assertEquals( router.match_entry(['e1']), set(['e2']) )
        self.assertEquals( router.match_entry(['e2']), set(['e3']) )
        self.assertEquals( router.match_entry(['e3']), set(['_end']) )

        self.assertEquals( router.match_entry(['_new', 'a']), set(['e1']) )
        self.assertEquals( router.match_entry(['_new', 'e2']), set(['e1', 'e3']) )
        ret = router.match_entry(['_new', 'e2', 'e3'])


    def test_next_multi(self):
        router = Router(
            Route().any('_new').next('e1', 'e1.1', 'e1.2' ),
            Route().any('e1').next('e2', 'e2.1'),
            Route().any('e1.1').next('e2', '_end'),
            Route().any('e1.2').next('e2.1', '_end'),
            Route().any('e2').next('_end'),
            Route().any('e2.1').next('_end'),
        )

        self.assertEquals( router.match_entry(['_new']), set(['e1', 'e1.1', 'e1.2']) )
        self.assertEquals( router.match_entry(['e1']), set(['e2.1', 'e2']))
        self.assertEquals( router.match_entry(['e1.1']), set(['e2', '_end']) )
        self.assertEquals( router.match_entry(['e1.2']), set(['e2.1', '_end']) )
        self.assertEquals( router.match_entry(['e2']), set(['_end']))
        self.assertEquals( router.match_entry(['e2.1']), set(['_end']))


    def test_exact_routing(self):
        router = Router(
            Route().any('_new').next('e1', 'e1.1', 'e1.2', 'e1.3'),
            Route().exact('e1.1', 'e1.2').next('e2'),
            Route().any('e1', 'e1.3').next('e2'),
            Route().any('e2').next('end'),
        )

        self.assertEquals( router.match_entry( ['_new']), set(['e1', 'e1.1', 'e1.2', 'e1.3']) )
        self.assertEquals( router.match_entry( ['e1.1', 'e1.2'] ), set(['e2']))
        self.assertEquals( router.match_entry( ['e1.3'] ), set(['e2']) )
        self.assertEquals( router.match_entry( ['e1'] ), set(['e2']) )
        self.assertEquals( router.match_entry( ['e2'] ), set(['end']) )


        self.assertEquals( router.match( ['_new']), set(['e1', 'e1.1', 'e1.2', 'e1.3']) )
        self.assertEquals( router.match( ['e1.1', 'e1.2'] ), set(['e2']))
        self.assertEquals( router.match( ['e1.3'] ), set(['e2']) )
        self.assertEquals( router.match( ['e1'] ), set(['e2']) )
        self.assertEquals( router.match( ['e2'] ), set(['end']) )


    def test_match(self):
        router = Router(
            Route().any('_new').next('check'),
            Route().any('check').next('not_pass').test( lambda d: d.get('score') < 60  ),
            Route().any('check').next('pass').test( lambda d: d.get('score') >= 60 ),
        )

        self.assertEquals( router.match( ['check'], {'score': 60}), set(['pass']) )
        self.assertEquals( router.match( ['check'], {'score': 100}), set(['pass']) )
        self.assertEquals( router.match( ['check'], {'score': 59}), set(['not_pass']) )
        self.assertEquals( router.match( ['check'], {'score': -60}), set(['not_pass']) )

    def test_involves_decendants(self):
        router = Router(
            Route().any('_new').next('check', 'parent'),
            Route().any('check').next('pass', 'not_pass'),
            Route().any('p').next('cA', 'cB'),
            Route().any('cA').next('cA.1'),
            Route().any('cA.1').next('cA.1.1', 'cA.1.2'),
            Route().any('cB').next('cB.1'),
            Route().any('cB.1').next('cB.1.1', 'cB.1.2'),
            Route().exact('cA.1.1', 'cA.1.2').next('_end'),
            Route().any('pass', 'not_pass').next('_end'),
        )
        #import ipdb; ipdb.set_trace()
        s = router.involve_decendants('p')

        self.assertTrue( 'check' not in s)
        self.assertTrue( 'pass' not in s)
        self.assertTrue( 'not_pass' not in s)
        
        self.assertTrue( 'cA' in s)
        self.assertTrue( 'cA.1' in s)
        self.assertTrue( 'cA.1.1' in s)
        self.assertTrue( 'cA.1.2' in s)

        self.assertTrue( 'cB' in s)
        self.assertTrue( 'cB.1' in s)
        self.assertTrue( 'cB.1.1' in s)
        self.assertTrue( 'cB.1.2' in s)

        self.assertTrue( '_end' in s)

    def test_choices(self):
        router = Router(
            Route().any('_new').next('check'),
            Route().any('check').next('not_pass').test( lambda d: d.get('score') < 60  ),
            Route().any('check').next('pass').test( lambda d: d.get('score') >= 60 ),
            Route().any('pass', 'not_pass').next('_end'),
        )

        #import ipdb; ipdb.set_trace()
        s = router.choices('check')
        #print s
        self.assertTrue( 'pass' in s)
        self.assertTrue( 'not_pass' in s)

        s1 = router.choices('pass')
        self.assertTrue( '_end' in s1)

        s2 = router.choices('not_pass')
        self.assertTrue( '_end' in s2)        
        

class RouteTest(TestCase):
    def test_exact(self):
        self.assertEqual( Route().exact('a', 'b', 'c', 'd', 'e')._in, 
                Exact('a', 'b', 'c', 'd', 'e') )
        self.assertNotEqual( Route().exact('a', 'b', 'c', 'd', 'e')._in, 
                Exact('a', 'b', 'c', ) )

    def test_any(self):
        self.assertEqual( Route().any('a', 'b', 'c', 'd', 'e')._in, 
            Any('a', 'b', 'c', 'd', 'e') )
        self.assertNotEqual( Route().any('a', 'b', 'c', 'd', 'e')._in, 
            Any('a', 'b') )


class EntryMatcherTest(TestCase):

    def test_iterator(self):
        any = Any('a', 'b', 'c')
        i = 0
        l = ['a', 'b', 'c']

        for s in any:
            self.assertTrue( s in l )
            l.remove(s)
        self.assertEquals( len(l), 0 )
        
    def test_eq(self):
        a = Exact('a', 'b')
        a1 = Exact('a', 'b')
        a2 = Any('a', 'b')

        #test __eq__
        self.assertEquals(a , a1)
        self.assertFalse(a == a2)
        #test __ne__
        self.assertFalse(a != a1)
        self.assertNotEquals(a , a2)

        

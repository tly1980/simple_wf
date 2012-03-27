"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from warehouse.wf.statemachine import Route, Router, Any, Exact, always_pass


class RouterTest(TestCase):
    def test_match_entry(self):
        router = Router(
            Route().any('_new').next('e1'),
            Route().any('e1').next('e2'),
            Route().any('e2').next('e3'),
            Route().any('e3').next('_end'),
        )

        self.assertEquals(router.match_entry(['_new']), set(['e1']))
        self.assertEquals(router.match_entry(['e1']), set(['e2']))
        self.assertEquals(router.match_entry(['e2']), set(['e3']))
        self.assertEquals(router.match_entry(['e3']), set(['_end']))

        self.assertEquals(router.match_entry(['_new', 'a']), set(['e1']))
        self.assertEquals(router.match_entry(['_new', 'e2']), set(['e1', 'e3']))
        self.assertEquals(router.match_entry(['_new', 'e2', 'e3']), set(['e1', 'e3', '_end']))

        router = Router(
            Route().any('_new').next('a', 'b', 'c', 'd'),
            Route().exact('a', 'b').next('ab'),
            Route().exact('a', 'c').next('ac'),
            Route().exact('b', 'c').next('bc'),
            Route().any('d').next('_end'),
        )

        self.assertEquals(router.match_entry(['a', 'b', 'c', 'd']), set(['ab', 'ac', 'bc', '_end']))

    def test_next_multi(self):
        router = Router(
            Route().any('_new').next('e1', 'e1.1', 'e1.2'),
            Route().any('e1').next('e2', 'e2.1'),
            Route().any('e1.1').next('e2', '_end'),
            Route().any('e1.2').next('e2.1', '_end'),
            Route().any('e2').next('_end'),
            Route().any('e2.1').next('_end'),
        )

        self.assertEquals(router.match_entry(['_new']), set(['e1', 'e1.1', 'e1.2']))
        self.assertEquals(router.match_entry(['e1']), set(['e2.1', 'e2']))
        self.assertEquals(router.match_entry(['e1.1']), set(['e2', '_end']))
        self.assertEquals(router.match_entry(['e1.2']), set(['e2.1', '_end']))
        self.assertEquals(router.match_entry(['e2']), set(['_end']))
        self.assertEquals(router.match_entry(['e2.1']), set(['_end']))

    def test_exact_routing(self):
        router = Router(
            Route().any('_new').next('e1', 'e1.1', 'e1.2', 'e1.3'),
            Route().exact('e1.1', 'e1.2').next('e2'),
            Route().any('e1', 'e1.3').next('e2'),
            Route().any('e2').next('end'),
        )

        self.assertEquals(router.match_entry(['_new']), set(['e1', 'e1.1', 'e1.2', 'e1.3']))
        self.assertEquals(router.match_entry(['e1.1', 'e1.2']), set(['e2']))
        self.assertEquals(router.match_entry(['e1.3']), set(['e2']))
        self.assertEquals(router.match_entry(['e1']), set(['e2']))
        self.assertEquals(router.match_entry(['e2']), set(['end']))

        self.assertEquals(router.match(['_new']), set(['e1', 'e1.1', 'e1.2', 'e1.3']))
        self.assertEquals(router.match(['e1.1', 'e1.2']), set(['e2']))
        self.assertEquals(router.match(['e1.3']), set(['e2']))
        self.assertEquals(router.match(['e1']), set(['e2']))
        self.assertEquals(router.match(['e2']), set(['end']))

    def test_match(self):
        router = Router(
            Route().any('_new').next('check'),
            Route().any('check').next('not_pass').test(lambda d: d.get('score') < 60),
            Route().any('check').next('pass').test(lambda d: d.get('score') >= 60),
        )

        self.assertEquals(router.match(['check'], {'score': 60}), set(['pass']))
        self.assertEquals(router.match(['check'], {'score': 100}), set(['pass']))
        self.assertEquals(router.match(['check'], {'score': 59}), set(['not_pass']))
        self.assertEquals(router.match(['check'], {'score': -60}), set(['not_pass']))

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
        
        s = router.involve_decendants('p')

        self.assertTrue('check' not in s)
        self.assertTrue('pass' not in s)
        self.assertTrue('not_pass' not in s)

        self.assertTrue('cA' in s)
        self.assertTrue('cA.1' in s)
        self.assertTrue('cA.1.1' in s)
        self.assertTrue('cA.1.2' in s)

        self.assertTrue('cB' in s)
        self.assertTrue('cB.1' in s)
        self.assertTrue('cB.1.1' in s)
        self.assertTrue('cB.1.2' in s)

        self.assertTrue('_end' in s)

    def test_involves_decendants2(self):
        router = Router(
            Route().any('_new').next('a'),
            Route().any('a').next('b', 'c'),
            Route().any('b').next('d'),
            Route().any('d').next('_end'),
            Route().any('c').next('_end'),
        )
        s = router.involve_decendants('a')
        self.assertEqual(s, set(['b', 'c', 'd', '_end']))
        s = router.involve_decendants('b')
        self.assertEqual(s, set(['d', '_end']))

    def test_choices(self):
        router = Router(
            Route().any('_new').next('check'),
            Route().any('check').next('not_pass').test(lambda d: d.get('score') < 60),
            Route().any('check').next('pass').test(lambda d: d.get('score') >= 60),
            Route().any('pass', 'not_pass').next('_end'),
        )

        #import ipdb; ipdb.set_trace()
        s = router.choices('check')
        #print s
        self.assertTrue('pass' in s)
        self.assertTrue('not_pass' in s)

        s1 = router.choices('pass')
        self.assertTrue('_end' in s1)

        s2 = router.choices('not_pass')
        self.assertTrue('_end' in s2)

    def test_entries_involves_andjoin(self):
        #ret should contains all the multi (len > 1) input in exact()

        # case1
        router = Router(
            Route().any('_new').next('a1', 'a2'),
            Route().exact('a1', 'a2').next('b1', 'b2'),
            Route().exact('b1').next('_end'),
            Route().exact('b2').next('_end'),
        )

        ret = router.entries_involves_andjoin()
        #b1 b2 should not in
        self.assertEquals(ret, set(['a1', 'a2']))

        # case 2
        router = Router(
            Route().any('_new').next('a1', 'a2', 'a3'),
            Route().exact('a1', 'a2').next('b1',),
            Route().exact('a2', 'a3').next('b2'),
            Route().any('b1', 'b2').next('_end'),
        )

        ret = router.entries_involves_andjoin()
        self.assertEquals(ret, set(['a1', 'a2', 'a3']))

        # case 3
        router = Router(
            Route().any('_new').next('a1', 'a2', 'a3'),
            Route().exact('a1', 'a2').next('b1',),
            Route().exact('a2', 'a3').next('b2'),
            Route().any('b1', 'b2').next('_end'),
        )

        ret = router.entries_involves_andjoin()
        self.assertEquals(ret, set(['a1', 'a2', 'a3']))

        # case 4
        router = Router(
            Route().any('_new').next('a1', 'a2', 'a3'),
            Route().exact('a1', 'a2').next('b1',),
            Route().exact('a2', 'a3').next('b2'),
            Route().exact('b1', 'b2').next('_end'),
        )

        ret = router.entries_involves_andjoin()
        self.assertEquals(ret, set(['a1', 'a2', 'a3', 'b1', 'b2']))

    def test_entries_involves_andsplit(self):
        #ret should contains all the multi (len > 1) ouput in next()

        #case1
        router = Router(
            Route().any('_new').next('a1', 'a2'),
            Route().any('a1', 'a2').next('b1'),
            Route().any('b1').next('c1', 'c2'),
            Route().any('c1',).next('_end'),
            Route().any('c2',).next('_end'),
        )

        ret = router.entries_involves_andsplit()
        self.assertEquals(ret, set(['a1', 'a2', 'c1', 'c2']))


class RouteTest(TestCase):
    def test_exact(self):
        r1 = Route().exact('a', 'b', 'c', 'd', 'e')
        self.assertEqual(len(r1.input().entries), 5)
        self.assertEqual(r1.input(), Exact('a', 'b', 'c', 'd', 'e'))
        self.assertNotEqual(r1.input(), Exact('a', 'b', 'c', ))

    def test_any(self):
        self.assertEqual(Route().any('a', 'b', 'c', 'd', 'e')._in,
            Any('a', 'b', 'c', 'd', 'e'))
        self.assertNotEqual(Route().any('a', 'b', 'c', 'd', 'e')._in,
            Any('a', 'b'))

    def test_is_andjoin(self):
        r1 = Route().exact('a', 'b', 'c', 'd', 'e')
        self.assertTrue(r1.is_andjoin())

        r2 = Route().exact('a')
        self.assertFalse(r2.is_andjoin())

        r3 = Route().any('a', 'b', 'c')
        self.assertFalse(r3.is_andjoin())

        r4 = Route().any('a')
        self.assertFalse(r4.is_andjoin())

    def test_is_andsplit(self):
        r1 = Route().next('a', 'b', 'c', 'd', 'e')
        self.assertTrue(r1.is_andsplit())

        r3 = Route().next('a', 'b')
        self.assertTrue(r3.is_andsplit())

        r2 = Route().next('a')
        self.assertFalse(r2.is_andsplit())

    def test_test(self):
        r1 = Route()
        self.assertEquals(always_pass, r1.test())
        self.assertTrue(r1.match_data({}))
        self.assertTrue(r1.match_data(None))

        gt1 = lambda a: a > 1
        r1.test(gt1)
        self.assertTrue(gt1, r1.test())
        self.assertTrue(r1.match_data(2))
        self.assertFalse(r1.match_data(1))


class EntryMatcherTest(TestCase):

    def test_iterator(self):
        any = Any('a', 'b', 'c')
        l = ['a', 'b', 'c']

        for s in any:
            self.assertTrue(s in l)
            l.remove(s)
        self.assertEquals(len(l), 0)

    def test_eq(self):
        a = Exact('a', 'b')
        a1 = Exact('a', 'b')
        a2 = Any('a', 'b')

        #test __eq__
        self.assertEquals(a, a1)
        self.assertFalse(a == a2)
        #test __ne__
        self.assertFalse(a != a1)
        self.assertNotEquals(a, a2)

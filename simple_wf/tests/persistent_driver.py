from django.test import TestCase
from warehouse.wf.persistent_driver import MemPersistentDriver
from warehouse.wf.models import DJPersistentDriver
from warehouse.wf.exception import (EntryException,
        MultiEntryReturn, EntryAlreadyActivated, EntryNotActivated)

from ..models import TransitionLog
from django.contrib.auth.models import User


class EntryExceptionTest(TestCase):
    def test_EntryException(self):
        e = EntryException('a', 'b', 'c')
        self.assertEqual(e.entry_set, set(['a', 'b', 'c']))

        e = MultiEntryReturn('a', 'b', 'c', entry_set=['d', 'e', 'a'])
        self.assertEqual(e.entry_set, set(['a', 'b', 'c', 'd', 'e']))

        self.assertEqual(repr(e),
            "MultiEntryReturn: set(['a', 'c', 'b', 'e', 'd'])")
        self.assertEqual('%s' % e,
            "MultiEntryReturn: set(['a', 'c', 'b', 'e', 'd'])")


class MemPersistentDriverTest(TestCase):
    def setUp(self):
        self.p_driver = MemPersistentDriver('test')

    def test_activate(self):
        self.p_driver.activate('a')

        self.assertEquals(self.p_driver.activated_set(), set(['a']))
        self.assertRaises(EntryAlreadyActivated, self.p_driver.activate, 'a')

        self.p_driver.activate('b')
        self.assertEquals(self.p_driver.activated_set(), set(['a', 'b']))
        self.assertRaises(EntryAlreadyActivated, self.p_driver.activate, 'b')

    def test_complete_exception(self):
        self.assertRaises(EntryNotActivated, self.p_driver.complete, 'e1')
        self.assertRaises(EntryNotActivated, self.p_driver.complete, 'e2')
        self.assertRaises(EntryNotActivated, self.p_driver.complete, 'e3')

    def test_complete(self):
        self.p_driver.activate('a')
        self.assertEquals(self.p_driver.activated_set(), set(['a']))
        self.p_driver.complete('a')
        self.assertEquals(self.p_driver.activated_set(), set([]))
        self.assertEquals(self.p_driver.completed_set(), set(['a']))

        self.p_driver.activate('b')
        self.assertEquals(self.p_driver.activated_set(), set(['b']))
        self.p_driver.complete('b')
        self.assertEquals(self.p_driver.activated_set(), set([]))
        self.assertEquals(self.p_driver.completed_set(), set(['a', 'b']))

        self.p_driver.activate('c')
        self.assertEquals(self.p_driver.activated_set(), set(['c']))
        self.p_driver.complete('c', True)
        self.assertEquals(self.p_driver.activated_set(), set([]))
        self.assertEquals(self.p_driver.completed_set(), set(['a', 'b']))
        self.assertEquals(self.p_driver.completed_set(True), set(['c']))

        self.p_driver.activate('d')
        self.assertEquals(self.p_driver.activated_set(), set(['d']))
        self.p_driver.complete('d', True)
        self.assertEquals(self.p_driver.activated_set(), set([]))
        self.assertEquals(self.p_driver.completed_set(), set(['a', 'b']))
        self.assertEquals(self.p_driver.completed_set(True), set(['c', 'd']))

        self.p_driver.activate('e')
        self.p_driver.activate('f')
        self.assertEquals(self.p_driver.activated_set(), set(['e', 'f']))

        self.p_driver.complete('e', True)
        self.assertEquals(self.p_driver.activated_set(), set(['f']))
        self.p_driver.complete('f', True)

        self.assertEquals(self.p_driver.completed_set(), set(['a', 'b']))
        self.assertEquals(self.p_driver.completed_set(True),
                        set(['c', 'd', 'e', 'f']))

    def test_disable_andjoin(self):
        self.p_driver.activate('a')
        self.p_driver.activate('b')
        self.p_driver.complete('a', True)
        self.p_driver.complete('b', True)
        self.assertEquals(self.p_driver.completed_set(), set([]))
        self.assertEquals(self.p_driver.completed_set(True), set(['a', 'b']))
        self.p_driver.disable_andjoin(['a'])
        self.assertEquals(self.p_driver.completed_set(), set(['a']))
        self.assertEquals(self.p_driver.completed_set(True), set(['b']))
        self.p_driver.disable_andjoin(['b'])
        self.assertEquals(self.p_driver.completed_set(), set(['a', 'b']))
        self.assertEquals(self.p_driver.completed_set(True), set([]))

    def test_disable_andjoin_batch(self):
        self.p_driver.activate('a')
        self.p_driver.activate('b')
        self.p_driver.complete('a', True)
        self.p_driver.complete('b', True)
        self.p_driver.disable_andjoin(['a', 'b'])
        self.assertEquals(self.p_driver.completed_set(), set(['a', 'b']))
        self.assertEquals(self.p_driver.completed_set(True), set([]))


class DjangoPersistentDriverTest(MemPersistentDriverTest):
    def setUp(self):
        user = User.objects.create(username='wf_user')
        self.p_driver = DJPersistentDriver(operator=user)

    def tearDown(self):
        self.print_log()

    def print_log(self):
        for l in TransitionLog.objects.all():
            print l

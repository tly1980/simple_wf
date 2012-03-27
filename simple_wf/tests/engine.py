from django.test import TestCase
from warehouse.wf.engine import MemPersistentDriver, WorkflowEngine
from warehouse.wf.statemachine import Router, Route


class MemPersistentDriverTest(TestCase):
    def setUp(self):
        self.p_driver = MemPersistentDriver('test')

    def test_activate(self):
        self.p_driver.activate('a')
        self.assertEquals(self.p_driver.activated_set(), set(['a']))
        self.p_driver.activate('b')
        self.assertEquals(self.p_driver.activated_set(), set(['a', 'b']))

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


class WorkflowEngineTest(TestCase):

    def setUp(self):
        self.router = Router()
        self.wf_engine = WorkflowEngine(MemPersistentDriver('test'),
             self.router)

    def test_router(self):
        r2 = Router()
        self.assertEqual(self.wf_engine.router(), self.router)
        self.assertEqual(self.wf_engine.router(r2), self.wf_engine)
        self.assertEqual(self.wf_engine.router(), r2)

    def test_todo(self):
        router = Router(
            Route().any('_new').next('e1'),
            Route().any('e1').next('e2'),
            Route().any('e2').next('e3'),
            Route().any('e3').next('_end'),
        )

        self.wf_engine.router(router)
        self.assertEqual(self.wf_engine.todo_set(), set(['_new']))
        self.wf_engine.start()
        self.assertEqual(self.wf_engine.todo_set(), set(['e1']))
        self.wf_engine.complete('e1')
        self.assertEqual(self.wf_engine.todo_set(), set(['e2']))
        self.wf_engine.complete('e2')
        self.assertEqual(self.wf_engine.todo_set(), set(['e3']))
        self.wf_engine.complete('e3')
        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))

    def test_todo1(self):
        router = Router(
            Route().any('_new').next('e1', 'e2'),
            Route().exact('e1', 'e2').next('e3'),
            Route().any('e3').next('_end'),
        )

        self.wf_engine.router(router)
        self.wf_engine.start()
        self.assertEqual(self.wf_engine.todo_set(), set(['e1', 'e2']))
        self.wf_engine.complete('e1')
        self.assertEqual(self.wf_engine.todo_set(), set(['e2']))
        self.wf_engine.complete('e2')
        self.assertEqual(self.wf_engine.todo_set(), set(['e3']))
        self.wf_engine.complete('e3')
        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))

    def test_todo2(self):
        router = Router(
            Route().any('_new').next('e0'),
            Route().any('e0').next('e1', 'e2', 'e3'),
            Route().exact('e1', 'e2').next('e4'),
            Route().any('e3').next('e0'),
            Route().any('e4').next('_end'),
        )

        self.wf_engine.router(router)
        self.wf_engine.start()
        self.assertEqual(self.wf_engine.todo_set(), set(['e0']))

        self.wf_engine.complete('e0')
        self.assertEqual(self.wf_engine.todo_set(), set(['e1', 'e2', 'e3']))
        self.wf_engine.complete('e1')
        self.wf_engine.complete('e2')
        self.assertEqual(self.wf_engine.todo_set(), set(['e3', 'e4']))
        # FIXME!!
        #self.wf_engine.complete('e3')
        #self.assertEqual(self.wf_engine.todo_set(), set(['e0']))

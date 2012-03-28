from django.test import TestCase
from ..engine import WorkflowEngine
from ..persistent_driver import MemPersistentDriver
from ..statemachine import Router, Route
from ..exception import EntryNotActivated
from ..models import DJPersistentDriver


class WorkflowEngineTest(TestCase):

    def setUp(self):
        self.router = Router()
        #self.wf_engine = WorkflowEngine(MemPersistentDriver('test'),
        #     self.router)
        self.wf_engine = WorkflowEngine(DJPersistentDriver(), self.router)

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
        self.assertEqual(self.wf_engine.todo_set(), set([]))
        #self.assertRaises(EntryNotActivated, self.wf_engine.complete, 'e1')
        with self.assertRaises(EntryNotActivated):
            self.wf_engine.complete('e1')

        self.assertRaises(EntryNotActivated, self.wf_engine.complete, 'e1')
        self.assertRaises(EntryNotActivated, self.wf_engine.complete, 'e2')
        self.assertRaises(EntryNotActivated, self.wf_engine.complete, 'e3')
        self.assertRaises(EntryNotActivated, self.wf_engine.complete, 'e4')
        self.assertRaises(EntryNotActivated,
                    self.wf_engine.complete, ('_end',))

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
        
        self.wf_engine.complete('e3')
        self.assertEqual(self.wf_engine.todo_set(), set(['e0']))

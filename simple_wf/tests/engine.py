from django.test import TestCase
from ..engine import WorkflowEngine
# from ..persistent_driver import MemPersistentDriver
from ..statemachine import Router, Route
from ..exception import EntryNotActivated
from ..models import DJPersistentDriver
from ..models import TransitionLog
from django.contrib.auth.models import User


class WorkflowEngineTest(TestCase):

    def setUp(self):
        self.router = Router()
        user = User.objects.create(username='wf_user')
        self.wf_engine = WorkflowEngine(DJPersistentDriver(operator=user), self.router)

    def tearDown(self):
        self.print_log()

    def print_log(self):
        for l in TransitionLog.objects.all():
            print l

    def test_router(self):
        r2 = Router()
        self.assertEqual(self.wf_engine.router(), self.router)
        self.assertEqual(self.wf_engine.router(r2), self.wf_engine)
        self.assertEqual(self.wf_engine.router(), r2)

    def test_complete_EntryNotActivated(self):
        router = Router(
            Route().any('_new').next('e1'),
            Route().any('e1').next('e2'),
            Route().any('e2').next('e3'),
            Route().any('e3').next('_end'),
        )
        self.wf_engine.router(router)

        self.assertRaises(EntryNotActivated, self.wf_engine.complete, '_new')
        self.assertRaises(EntryNotActivated, self.wf_engine.complete, 'e1')
        self.assertRaises(EntryNotActivated, self.wf_engine.complete, 'e2')
        self.assertRaises(EntryNotActivated, self.wf_engine.complete, 'e3')
        self.assertRaises(EntryNotActivated, self.wf_engine.complete, 'e4')
        self.assertRaises(EntryNotActivated,
                    self.wf_engine.complete, ('_end',))

    def test_todo(self):
        router = Router(
            Route().any('_new').next('e1'),
            Route().any('e1').next('e2'),
            Route().any('e2').next('e3'),
            Route().any('e3').next('_end'),
        )

        self.wf_engine.router(router)
        self.assertEqual(self.wf_engine.todo_set(), set([]))

        self.assertEqual(self.wf_engine.wf_state(), 'new')
        self.wf_engine.wf_start()
        self.assertEqual(self.wf_engine.wf_state(), 'started')

        self.assertEqual(self.wf_engine.todo_set(), set(['e1']))
        self.wf_engine.complete('e1')
        self.assertEqual(self.wf_engine.todo_set(), set(['e2']))
        self.wf_engine.complete('e2')
        self.assertEqual(self.wf_engine.todo_set(), set(['e3']))
        self.wf_engine.complete('e3')
        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))

        #wf should close automatically when _end completed
        self.wf_engine.complete('_end')
        self.assertEqual(self.wf_engine.wf_state(), 'closed')

    def test_todo1(self):
        router = Router(
            Route().any('_new').next('e1', 'e2'),
            Route().exact('e1', 'e2').next('e3'),
            Route().any('e3').next('_end'),
        )

        self.wf_engine.router(router)
        self.wf_engine.wf_start()
        self.assertEqual(self.wf_engine.todo_set(), set(['e1', 'e2']))
        self.wf_engine.complete('e1')
        self.assertEqual(self.wf_engine.todo_set(), set(['e2']))
        self.wf_engine.complete('e2')
        self.assertEqual(self.wf_engine.todo_set(), set(['e3']))
        self.wf_engine.complete('e3')
        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))

        #wf should close automatically when _end completed
        self.wf_engine.complete('_end')
        self.assertEqual(self.wf_engine.wf_state(), 'closed')

    def test_todo2(self):
        router = Router(
            Route().any('_new').next('e0'),
            Route().any('e0').next('e1', 'e2', 'e3'),
            Route().exact('e1', 'e2').next('e4'),
            Route().any('e3').next('e0'),
            Route().any('e4').next('_end'),
        )

        self.wf_engine.router(router)
        self.wf_engine.wf_start()
        self.assertEqual(self.wf_engine.todo_set(), set(['e0']))

        self.wf_engine.complete('e0')
        self.assertEqual(self.wf_engine.todo_set(), set(['e1', 'e2', 'e3']))
        self.wf_engine.complete('e1')
        self.wf_engine.complete('e2')
        self.assertEqual(self.wf_engine.todo_set(), set(['e3', 'e4']))

        #e3 should restart the e0
        self.wf_engine.complete('e3')
        self.assertEqual(self.wf_engine.todo_set(), set(['e0']))

        self.wf_engine.complete('e0')
        self.assertEqual(self.wf_engine.todo_set(), set(['e1', 'e2', 'e3']))
        self.wf_engine.complete('e1')
        self.wf_engine.complete('e2')
        self.assertEqual(self.wf_engine.todo_set(), set(['e3', 'e4']))
        self.wf_engine.complete('e4')
        self.assertEqual(self.wf_engine.todo_set(), set(['_end', 'e3']))

        #wf should close automatically when _end completed
        self.wf_engine.complete('_end')
        self.assertEqual(self.wf_engine.wf_state(), 'closed')

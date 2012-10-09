from django.test import TestCase
from ..engine import WorkflowEngine
# from ..persistent_driver import MemPersistentDriver
from ..statemachine import Router, Route

from ..models import DJPersistentDriver

from django.contrib.auth.models import User


class SimpleConditionRoutingTest(TestCase):
    def setUp(self):
        self.router = Router()
        user = User.objects.create(username='wf_user')
        self.wf_engine = WorkflowEngine(DJPersistentDriver(operator=user), self.router)

        router = Router(
            Route().any('_new').next('check'),
            Route().any('check').next('pass').test(lambda d: d.get('score') >= 60),
            Route().any('check').next('not_pass').test(lambda d: d.get('score') < 60),
            Route().any('pass').next('_end'),
            Route().any('not_pass').next('_end'),
        )

        self.wf_engine.router(router)

    def test_pass(self):
        self.wf_engine.wf_start()

        # the first todo should be "check"
        self.assertEqual(self.wf_engine.todo_set(), set(['check']))

        # provide the score to the complete function, it will choose next
        # appropriate workflow activity
        self.wf_engine.complete('check', data={'score': 60})

        # when score is less than 60, the only proper activity is pass
        self.assertEqual(self.wf_engine.todo_set(), set(['pass']))

        self.wf_engine.complete('pass')

        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))
        #wf should close automatically when _end completed
        self.wf_engine.complete('_end')
        self.assertEqual(self.wf_engine.wf_state(), 'closed')

    def test_not_pass(self):
        self.wf_engine.wf_start()

        # the first todo should be "check"
        self.assertEqual(self.wf_engine.todo_set(), set(['check']))

        # provide the score to the complete function, it will choose next
        # appropriate workflow activity
        self.wf_engine.complete('check', data={'score': 59})

        # when score is greater than 60, the only proper activity is pass
        self.assertEqual(self.wf_engine.todo_set(), set(['not_pass']))

        # now you should do sth to handle
        self.wf_engine.complete('not_pass')
        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))

        #wf should close automatically when _end completed
        self.wf_engine.complete('_end')

        self.assertEqual(self.wf_engine.wf_state(), 'closed')
